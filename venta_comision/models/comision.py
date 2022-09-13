# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
import base64
import io
import xlrd

MESES = [
            ('1','Enero'),
            ('2','Febrero'),
            ('3','Marzo'),
            ('4','Abril'),
            ('5','Mayo'),
            ('6','Junio'),
            ('7','Julio'),
            ('8','Agosto'),
            ('9','Septiembre'),
            ('10','Octubre'),
            ('11','Noviembre'),
            ('12','Diciembre'),
        ]

TIPO_BONO_COMISION=[
            ('productividad', 'Bono Productividad'),
            ('comision', 'Comision')
        ]

class VentaComisionLine(models.Model):
    _name = "venta.comision.line"
    _description = "Comisiones Detalle"

    name = fields.Char(string='Factura', required=True)
    comision_id = fields.Many2one('venta.comision', string='Commission Reference', required=True, ondelete='cascade', index=True, copy=False)
    factura_id = fields.Many2one('account.move', string="Factura ID", readonly=True, states={'draft': [('readonly', False)]},)

    vendedor_id = fields.Many2one('res.users', string='Vendedor')
    almacen_id = fields.Many2one('stock.warehouse', string='Almacen')
    cliente_id = fields.Many2one(related='factura_id.partner_id', depends=['factura_id.partner_id'], store=True, string='Cliente', readonly=True)

    precio_sin_iva = fields.Float(string='Venta', readonly=True)
    costo = fields.Float(string='Costo', readonly=True)
    utilidad = fields.Float(string='Utilidad', readonly=True)
    porcentaje_utilidad = fields.Float(string='% Utilidad', readonly=True)


    pago_id = fields.Many2one('account.payment', string='Pago', readonly=True )
    pago_name = fields.Char(string='Referencia', readonly=True)
    pago_date = fields.Date(string='Pago Fecha', readonly=True)
    pago_monto = fields.Float(string='Pago Monto', readonly=True)
    pago_abono = fields.Float(string='Pago Abono', readonly=True)
    pago_anticipo = fields.Float(string='Pago Anticipo', readonly=True)
    exenciones_iva = fields.Float(string='Exenciones', readonly=True)
    retenciones_iva = fields.Float(string='Retenciones', readonly=True)
    nota_abono_monto = fields.Float(string='Abono', readonly=True)
    nota_credito_monto = fields.Float(string='Credito', readonly=True)
    iva = fields.Float(string='Iva', readonly=True)
    pago_total_sin_iva = fields.Float(string='Pago Total', readonly=True)
    comision = fields.Float(string='Comision', readonly=True)
    corresponde = fields.Boolean(string='Corresponde', default='False', readonly=True)

    currency_id = fields.Many2one(related='factura_id.currency_id', depends=['factura_id.currency_id'], store=True, string='Moneda', readonly=True)

    company_id = fields.Many2one(related='comision_id.company_id', string='Company', store=True, readonly=True, index=True)

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], related='comision_id.state', string='Order Status', readonly=True, copy=False, store=True, default='draft')

    tipo_bono_nomina = fields.Selection(
        selection = TIPO_BONO_COMISION,
        string="Tipo Bono Comision",
        required=True,
        default="productividad",
        readonly=True,
        help="Seleccione donde se realizara el cargo de la comision de venta, si es en el rubro de Bono de Productividad o en el de Comision en la Nomina de Bonos"
    )


class VentaComision(models.Model):
    _name = "venta.comision"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Comisiones'
    _order = 'id desc'

    name = fields.Char(string='Number', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))

    now = datetime.now()
    periodo = fields.Selection(MESES,string='Periodo',default=str(now.month), required=True, states={'draft': [('readonly', False)]},)
    ejercicio = fields.Integer(string='Ejercicio', default=now.year, required=True, states={'draft': [('readonly', False)]},)
    vendedor_id = fields.Many2many('res.users', string='Vendedor')

    company_id = fields.Many2one('res.company', string='Company', readonly=True, required=True, default=lambda self: self.env.company)


    ref = fields.Char(string='Referencia', copy=False)
    state = fields.Selection([
            ('draft', 'Draft'),
            ('done', 'Done'),
            ('cancel', 'Cancelled')
        ], string='Estatus', required=True, readonly=True, copy=False, tracking=True,
        default='draft')

    sales_commision_line = fields.One2many('venta.comision.line', 'comision_id', string='Comision Lineas', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True, auto_join=True)

    def action_confirmar(self):
        for doc in self:
            doc.state = 'done'

    def get_Listado_Vendedor_tienda(self, facturas_ids):
        #Consulta para listar a todos los Vendedores
        if not facturas_ids:
            return False
        query = """
            SELECT m.invoice_user_id, p.name, s.warehouse_id, sw.name, count(*)
            from account_move m
            join res_users u on u.id = m.invoice_user_id
            join res_partner p on p.id = u.partner_id
            join account_move_line md on md.move_id = m.id and md.product_id is not null
            LEFT OUTER JOIN sale_order_line_invoice_rel r1 on r1.invoice_line_id = md.id
            LEFT OUTER JOIN sale_order_line sl on sl.id = r1.order_line_id
            LEFT OUTER JOIN sale_order s on s.id = sl.order_id
            LEFT OUTER JOIN stock_warehouse sw on sw.id = s.warehouse_id
            WHERE m.id IN %s --and m.partner_id = 11741
            --and u.id = 148
            group by m.invoice_user_id, p.name, s.warehouse_id, sw.name
            order by p.name
        """
        self._cr.execute(query, (tuple(facturas_ids),))
        lista = []
        listas_unica_factura = []
        for r in self._cr.fetchall():
            lista_vendedores = {}
            lista_vendedores['vendedor_id'] = r[0]
            lista_vendedores['vendedor_name'] = r[1]
            lista_vendedores['almacen_id'] = r[2]
            lista_vendedores['almacen_name'] = r[3]
            vendedor_user = self.env["res.users"].browse(lista_vendedores['vendedor_id'])
            vendedor_comision = vendedor_user.comision_tabla_id
            #Consulta para listar a todos los clientes
            query = """
                SELECT m.invoice_user_id, p.name, m.partner_id, p2.name, p2.vat, m.id, count(*)
                from account_move m
                join res_users u on u.id = m.invoice_user_id
                join res_partner p on p.id = u.partner_id
                join res_partner p2 on p2.id = m.partner_id
                join account_move_line md on md.move_id = m.id and md.product_id is not null
                LEFT OUTER JOIN sale_order_line_invoice_rel r1 on r1.invoice_line_id = md.id
                LEFT OUTER JOIN sale_order_line sl on sl.id = r1.order_line_id
                LEFT OUTER JOIN sale_order s on s.id = sl.order_id
                LEFT OUTER JOIN stock_warehouse sw on sw.id = s.warehouse_id
                where m.id IN %s and m.invoice_user_id = %s and
                --m.id = 31124 and
                """ + ("s.warehouse_id=%s" if lista_vendedores['almacen_id'] else "s.warehouse_id is null") + """
                group by m.invoice_user_id, p.name, m.partner_id, p2.name, p2.vat, m.id
                order by p.name, p2.name, m.id
            """
            if lista_vendedores['almacen_id']:
                self._cr.execute(query, (tuple(facturas_ids), lista_vendedores['vendedor_id'], lista_vendedores['almacen_id']))
            else:
                self._cr.execute(query, (tuple(facturas_ids), lista_vendedores['vendedor_id']))

            #Lista de todas las facturas primero por vendedor, cliente, y facturas
            list_vend_cliente = []
            for vend_cliente in self._cr.fetchall():
                new = {
                    'vendedor_id': vend_cliente[1],
                    'cliente_id': vend_cliente[2],
                    'cliente_name': vend_cliente[3],
                    'cliente_nit': vend_cliente[4],
                    'factura_id': vend_cliente[5],
                }

                #El siguiente codigo me permite encontrar si alguna factura ya fue ingresada a la lista para ya no tomarla en cuenta.
                #Soluciona el problema cuando en ocaciones una linea del detalle de pedido no se factura, creando grupos de linea con almacen y otra sin almacen.
                encontrar_factura = False
                for busca_factura in listas_unica_factura:
                    if new['factura_id'] == busca_factura:
                        encontrar_factura = True

                if not encontrar_factura:
                    list_vend_cliente.append(new)
                    listas_unica_factura.append(new['factura_id'])
            lista_documentos = []

            vendedor_sub_total = {}
            vendedor_sub_total['precio_sin_iva'] = 0
            vendedor_sub_total['costo'] = 0
            vendedor_sub_total['utilidad'] = 0
            vendedor_sub_total['precio_sin_iva'] = 0
            vendedor_sub_total['pago_monto'] = 0
            vendedor_sub_total['pago_abono'] = 0
            vendedor_sub_total['pago_anticipo'] = 0
            vendedor_sub_total['comision'] = 0
            vendedor_sub_total['nota_credito_monto'] = 0
            vendedor_sub_total['nota_abono_monto'] = 0

            vendedor_sub_total['exenciones_iva'] = 0
            vendedor_sub_total['retenciones_iva'] = 0

            vendedor_sub_total['iva'] = 0
            vendedor_sub_total['pago_total_sin_iva'] = 0
            for s in list_vend_cliente:
                lista_clientes = {}
                lista_clientes['cliente_id'] = s['cliente_id']
                lista_clientes['cliente_name'] = s['cliente_name']
                lista_clientes['cliente_nit'] = s['cliente_nit']
                lista_clientes['factura_id'] = s['factura_id']

                facturas = self.env['account.move'].search([
                        ('invoice_user_id','=',lista_vendedores['vendedor_id']),
                        ('id','=',lista_clientes['factura_id']),
                        ('partner_id','=',lista_clientes['cliente_id'])
                        ])
                lista_facturas = []
                cliente_sub_total = {}
                cliente_sub_total['precio_sin_iva'] = 0
                cliente_sub_total['costo'] = 0
                cliente_sub_total['utilidad'] = 0
                cliente_sub_total['precio_sin_iva'] = 0
                cliente_sub_total['pago_monto'] = 0
                cliente_sub_total['pago_abono'] = 0
                cliente_sub_total['pago_anticipo'] = 0
                cliente_sub_total['nota_credito_monto'] = 0
                cliente_sub_total['nota_abono_monto'] = 0


                cliente_sub_total['exenciones_iva'] = 0
                cliente_sub_total['retenciones_iva'] = 0

                cliente_sub_total['comision'] = 0
                cliente_sub_total['iva'] = 0
                cliente_sub_total['pago_total_sin_iva'] = 0
                cliente_sub_total['comision'] = 0

                for factura in facturas:
                    costos = []
                    costo = 0
                    if vendedor_comision:
                        for detalle in factura.invoice_line_ids:
                            if vendedor_comision.producto_ids:
                                ids = [x.product_tmpl_id.id for x in vendedor_comision.producto_ids]
                                if detalle.product_id.product_tmpl_id.id in ids:
                                    producto_costo = detalle.costo
                                    producto_sin_iva = detalle.price_total / 1.12
                                    costos.append({'producto':detalle.product_id,'costo':producto_costo,'utilidad':abs((detalle.balance/1.12))-detalle.costo,'precio_sin_iva':producto_sin_iva})


                        lista_factura = {}
                        precio_sin_iva = factura.amount_untaxed
                        costo = sum(detalle.costo for detalle in factura.invoice_line_ids)
                        utilidad = precio_sin_iva - costo
                        porcentaje_utilidad = utilidad / precio_sin_iva

                        lista_factura['precio_sin_iva'] = precio_sin_iva
                        lista_factura['costo'] = costo
                        lista_factura['utilidad'] = utilidad
                        lista_factura['porcentaje_utilidad'] = porcentaje_utilidad
                        lista_factura['factura_id'] = factura.id
                        lista_factura['factura_diario'] = factura.journal_id.name
                        lista_factura['factura_name'] = factura.name
                        lista_factura['factura_partner_name'] = factura.partner_id.name
                        lista_factura['corresponde'] = (factura.invoice_user_id.id == factura.partner_id.user_id.id)
                        lista_factura['pago_monto'] = 0
                        lista_factura['pago_abono'] = 0
                        lista_factura['pago_anticipo'] = 0
                        lista_factura['nota_credito_monto'] = 0
                        lista_factura['nota_abono_monto'] = 0
                        lista_factura['exenciones_iva'] = 0
                        lista_factura['retenciones_iva'] = 0
                        lista_factura['iva'] = factura.sat_iva
                        lista_factura['comision'] = 0

                    pagos_ids = factura.get_pagos_aplicados_factura()
                    #print("-----------------------------------------------------------------------------")
                    for pago_cliente in pagos_ids:

                        account_lines = self.env['account.move.line'].browse(pago_cliente['id'])
                        ultimo_dia_pago = None
                        #print(pago_cliente['monto'])
                        for account_line in account_lines:
                            if account_line.payment_id:
                                #print("-------------------Siiiiiiiiiiiiiiiiiiiiii")
                                pago = self.env['account.payment'].browse(account_line.payment_id.id)
                                ultimo_dia_pago = pago.move_id.date
                                lista_factura['pago_id'] = pago.id
                                lista_factura['pago_name'] = pago.name
                                lista_factura['pago_date'] =  pago.move_id.date
                                if pago.tipo_pago == 'abono':
                                    lista_factura['pago_abono'] +=  pago_cliente['monto']
                                elif pago.tipo_pago == 'anticipo':
                                    lista_factura['pago_anticipo'] +=  pago_cliente['monto']
                                else:
                                    lista_factura['pago_monto'] +=  pago_cliente['monto']

                            else:
                                #print("-------------------Nooooooooooooooooooooooooo")
                                pago = self.env['account.move'].browse(account_line.move_id.id)
                                ultimo_dia_pago = pago.invoice_date

                                #Siguientes 2 Lineas debe aplicar solo para las facturas de punto de venta, porque no tienen pago, solo diario de pago.
                                #if lista_factura['pago_monto'] == 0:
                                #    lista_factura['pago_monto'] =  pago_cliente['monto']

                                if pago.journal_id.tipo_operacion in ('EXENIVA',):
                                    lista_factura['exenciones_iva'] = pago.amount_total
                                elif pago.journal_id.tipo_operacion in ('RETENIVA',):
                                    lista_factura['retenciones_iva'] = pago_cliente['monto']
                                elif pago.journal_id.tipo_documento in ('NABN',):
                                    lista_factura['nota_abono_monto'] = pago.amount_total
                                    lista_factura['iva'] = lista_factura['iva'] - (lista_factura['nota_abono_monto'] / (factura.sat_iva_porcentaje/100+1) * (factura.sat_iva_porcentaje/100))
                                elif pago.journal_id.tipo_documento in ('NCRE',):
                                    lista_factura['nota_credito_monto'] = pago.amount_total
                                    lista_factura['iva'] = lista_factura['iva'] - (lista_factura['nota_credito_monto'] / (factura.sat_iva_porcentaje/100+1) * (factura.sat_iva_porcentaje/100))
                                else:
                                    #lista_factura['pago_id'] = pago.id
                                    lista_factura['nota_sin_clasificar'] = pago.name
                                #lista_factura['pago_date'] = pago.date
                    lista_factura['pago_total_sin_iva'] = lista_factura['pago_monto'] + lista_factura['pago_anticipo'] + lista_factura['pago_abono'] + lista_factura['exenciones_iva'] + lista_factura['retenciones_iva'] - lista_factura['iva']


                    if vendedor_comision:

                        dias_plazo_pagos = self._getDiasPlazoPago(factura.invoice_payment_term_id.id)

                        last_month = factura.invoice_date + timedelta(days=dias_plazo_pagos) + timedelta(days=vendedor_comision.dias)
                        margen = 0
                        excepciones = 0
                        if vendedor_comision.aplicar_en == 'utilidad':
                            margen = lista_factura['utilidad'] - excepciones
                        else:
                            margen = lista_factura['pago_total_sin_iva']
                            if costos:
                                for ex in costos:
                                    excepciones += ex['precio_sin_iva']
                                margen = margen - excepciones
                        if last_month >= ultimo_dia_pago:
                            lista_factura['comision'] = margen * (vendedor_comision.porcentaje/100)
                            if costos:
                                for ex in costos:
                                    lista_factura['comision'] += ex['precio_sin_iva'] * (ex['producto'].product_tmpl_id.comision/100)
                        else:
                            if vendedor_comision.aplica_2Porcentaje:
                                lista_factura['comision'] = margen * (vendedor_comision.porcentaje2/100)
                                if costos:
                                    for ex in costos:
                                        lista_factura['comision'] += ex['precio_sin_iva'] * (ex['producto'].product_tmpl_id.comision/100)

                    cliente_sub_total['precio_sin_iva'] += lista_factura['precio_sin_iva']
                    cliente_sub_total['costo'] += lista_factura['costo']
                    cliente_sub_total['utilidad'] += lista_factura['utilidad']
                    #cliente_sub_total['precio_sin_iva'] += lista_factura['precio_sin_iva']
                    cliente_sub_total['pago_monto'] += lista_factura['pago_monto']
                    cliente_sub_total['pago_abono'] += lista_factura['pago_abono']
                    cliente_sub_total['pago_anticipo'] += lista_factura['pago_anticipo']
                    cliente_sub_total['nota_credito_monto'] += lista_factura['nota_credito_monto']
                    cliente_sub_total['nota_abono_monto'] += lista_factura['nota_abono_monto']

                    cliente_sub_total['exenciones_iva'] += lista_factura['exenciones_iva']
                    cliente_sub_total['retenciones_iva'] += lista_factura['retenciones_iva']

                    cliente_sub_total['iva'] += lista_factura['iva']
                    cliente_sub_total['pago_total_sin_iva'] += lista_factura['pago_total_sin_iva']
                    cliente_sub_total['comision'] += lista_factura['comision']

                    lista_facturas.append(lista_factura)


                vendedor_sub_total['precio_sin_iva'] += cliente_sub_total['precio_sin_iva']
                vendedor_sub_total['costo'] += cliente_sub_total['costo']
                vendedor_sub_total['utilidad'] += cliente_sub_total['utilidad']
                vendedor_sub_total['pago_monto'] += cliente_sub_total['pago_monto']
                vendedor_sub_total['pago_abono'] += cliente_sub_total['pago_abono']
                vendedor_sub_total['pago_anticipo'] += cliente_sub_total['pago_anticipo']
                vendedor_sub_total['nota_credito_monto'] += cliente_sub_total['nota_credito_monto']
                vendedor_sub_total['nota_abono_monto'] += cliente_sub_total['nota_abono_monto']

                vendedor_sub_total['exenciones_iva'] += cliente_sub_total['exenciones_iva']
                vendedor_sub_total['retenciones_iva'] += cliente_sub_total['retenciones_iva']

                vendedor_sub_total['iva'] += cliente_sub_total['iva']
                vendedor_sub_total['pago_total_sin_iva'] += cliente_sub_total['pago_total_sin_iva']
                vendedor_sub_total['comision'] += cliente_sub_total['comision']

                lista_clientes['lista_facturas'] = lista_facturas
                lista_clientes['cliente_sub_total'] = cliente_sub_total

                lista_documentos.append(lista_clientes)
            lista_vendedores['lista_documentos'] = lista_documentos
            lista_vendedores['vendedor_sub_total'] = vendedor_sub_total
            lista.append(lista_vendedores)
        return lista

    def _getDiasPlazoPago(self, pago_id):
        condicon_pago = self.env['account.payment.term'].browse(pago_id)
        dias = condicon_pago.line_ids.filtered(lambda line: line.value == 'balance').days
        return dias

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            seq_date = None
            if 'date_order' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date']))
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
                    'venta.comision', sequence_date=seq_date) or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('venta.comision', sequence_date=seq_date) or _('New')
        result = super(VentaComision, self).create(vals)
        return result

    def action_cargar_facturas(self):
        self.action_clean()
        # domain = [('type','in',('out_invoice','out_refund'))]
        # domain += [('state', '=', 'posted')]
        # domain += [('create_date', '<=', self.date)]
        # domain += [('invoice_payment_state', '=', 'paid')]
        #
        # facturas = self.env['account.move'].search(domain)

        i = 0
        #Consulta para ir a traer todas las facturas (ml.move_id), que fueron pagadas en el mes seleccionado.
        from calendar import monthrange
        from datetime import date
        mdays = monthrange(self.ejercicio,int(self.periodo))[1]
        date2 = date(self.ejercicio,int(self.periodo),mdays)

        query = """
            SELECT ml.move_id, max(apm.date) FechaMaxPago
            FROM account_move_line ml
            JOIN account_move m on ml.move_id = m.id
            JOIN account_partial_reconcile apr on apr.debit_move_id = ml.id
            JOIN account_move_line ml2 on apr.credit_move_id = ml2.id
            JOIN account_move m2 on ml2.move_id = m2.id
            JOIN account_journal j on m.journal_id = j.id
            LEFT OUTER JOIN account_payment ap on ap.id = ml2.payment_id
			JOIN account_move apm ON apm.payment_id = ap.id
            where (select internal_type from account_account where id = ml.account_id) = 'receivable'
            and m.payment_state in ('paid')
            and j.tipo_documento is not null
            and not exists (
            		select *
            		from venta_comision_line cd
            		join venta_comision c on c.id = cd.comision_id
            		where cd.factura_id = ml.move_id and c.state = 'done'
            )
            group by ml.move_id
            having max(apm.date) <= %s
        """
        self._cr.execute(query, (date2,))
        facturas_ids = [r[0] for r in self._cr.fetchall()]
        facturas = self.env['account.move'].browse(facturas_ids)
        print(facturas)

        lista_valores = self.get_Listado_Vendedor_tienda(facturas_ids)
        if not lista_valores:
            return True



        for vendedor in lista_valores:
            comision_line = {}


            #sheet_libro.write(fila, 0, vendedor['vendedor_name'])
            #sheet_libro.write(fila, 4, vendedor['almacen_name'])
            #sheet_libro.set_row(fila, cell_format=self.data_format1)


            for cliente in vendedor['lista_documentos']:

                #sheet_libro.write(fila, 0, cliente['cliente_nit'], self.bold)
                #sheet_libro.write(fila, 1, cliente['cliente_name'], self.bold)



                for factura in cliente['lista_facturas']:


                    #sheet_libro.write(fila, 0, factura['factura_id'])
                    #sheet_libro.write(fila, 1, factura['factura_diario'])
                    #sheet_libro.write(fila, 2, factura['factura_name'])
                    #sheet_libro.write(fila, 3, factura['factura_partner_name'])
                    comision_line['vendedor_id'] = vendedor['vendedor_id']
                    comision_line['almacen_id'] = vendedor['almacen_id']
                    comision_line['cliente_id'] = cliente['cliente_id']
                    comision_line['comision_id'] = self.id
                    comision_line['factura_id'] = factura['factura_id']
                    comision_line['name'] = factura['factura_name']
                    comision_line['precio_sin_iva'] = factura['precio_sin_iva']
                    comision_line['costo'] = factura['costo']
                    comision_line['utilidad'] = factura['utilidad']

                    comision_line['porcentaje_utilidad'] = factura['porcentaje_utilidad']

                    if 'pago_id' in factura:
                        comision_line['pago_id'] = factura['pago_id']
                        comision_line['pago_name'] = factura['pago_name']
                        comision_line['pago_date'] = factura['pago_date']
                    comision_line['pago_monto'] = factura['pago_monto']
                    comision_line['pago_abono'] = factura['pago_abono']
                    comision_line['pago_anticipo'] = factura['pago_anticipo']
                    comision_line['nota_credito_monto'] = factura['nota_credito_monto']
                    comision_line['nota_abono_monto'] = factura['nota_abono_monto']
                    comision_line['exenciones_iva'] = factura['exenciones_iva']
                    comision_line['retenciones_iva'] = factura['retenciones_iva']
                    comision_line['iva'] = factura['iva']
                    comision_line['pago_total_sin_iva'] = factura['pago_total_sin_iva']
                    comision_line['comision'] = factura['comision']
                    comision_line['corresponde'] = factura['corresponde']

                    vendedor_user = self.env["res.users"].browse(vendedor['vendedor_id'])
                    vendedor_comision = vendedor_user.comision_tabla_id
                    if vendedor_comision:
                        comision_line['tipo_bono_nomina'] = vendedor_comision.tipo_bono_nomina
                    self.env['venta.comision.line'].create(comision_line)



        return True

    def action_clean(self):
        for data in self:
            data.sales_commision_line.unlink()

    def export_xls(self):
        self.ensure_one()
        context = self._context
        data = {}
        data['venta_comision_id'] = self.id
        return self.env['ir.actions.report'].search([('report_name', '=', 'venta_comision.venta_comision_excel'),
				('report_type', '=', 'xlsx')], limit=1).report_action(self,data=data)

    def action_update_costo(self):
        facturas = self.env['account.move'].search([('id','=',27860)])
        i = 0
        for factura in facturas:
            i += 1
            for detalle in factura.invoice_line_ids:
                detalle._product_margin()

class VentaTablaComisiones(models.Model):
    _name = "venta.comision.tabla"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Tabla de Comisiones"

    name = fields.Char(string='Descripcion')
    active = fields.Boolean(string='Activo', default=True)
    dias = fields.Integer(string='Dias', default='90', help="Dias para aplicar comision despues de haber publicado la factura.")
    tipo_comision = fields.Selection([('porcentaje', 'Porcentaje'), ('categoria', 'Categoria de producto'),('producto','Producto')], string='Tipo de Comision', default='porcentaje')
    porcentaje = fields.Float(string='1 Porcentaje', help="Porcentaje que se aplica antes de los dias establecidos.",tracking=True)
    aplica_2Porcentaje = fields.Boolean(string='Aplica 2 porcentaje', default=False, help="Permite habilitar que se aplique el segundo % al superar los dias establecidos." ,tracking=True)
    porcentaje2 = fields.Float(string='2 Porcentaje', help="Porcentaje que se aplica despues de los dias establecidos.",tracking=True)
    aplicar_en = fields.Selection(
        selection=[('ventas', 'Ventas'),('utilidad', 'Utilidad')],
        string="Aplicar En",
        required=True,
        default="ventas",
        tracking=True
    )
    tipo_bono_nomina = fields.Selection(
        selection = TIPO_BONO_COMISION,
        string="Tipo Bono Comision",
        required=True,
        default="productividad",
        help="Seleccione donde se realizara el cargo de la comision de venta, si es en el rubro de Bono de Productividad o en el de Comision en la Nomina de Bonos"
    )
    comision_user_ids = fields.One2many('res.users', 'comision_tabla_id', string='Vendedores', readonly=True,tracking=True)
    producto_ids = fields.One2many('venta.comision.tabla.producto', 'tabla_comision_id', string='Productos',tracking=True)

    def load_exception(self):
        new_wizard = self.env['wizard.excepcion.comisiones'].create({'name': 'Excepciones'})
        view_id = self.env.ref('venta_comision.wizard_excepcion_comisiones').id

        return {
            'type': 'ir.actions.act_window',
            'name': _('Carga de Excepciones'),
            'view_mode': 'form',
            'res_model': 'wizard.excepcion.comisiones',
            'target': 'new',
            'res_id': new_wizard.id,
            'views': [[view_id, 'form']],
        }

class VentaTablaComisionProducto(models.Model):
    _name = "venta.comision.tabla.producto"
    _description = "Tabla de Comisiones Producto"

    name = fields.Char(string='Descripcion', default='Producto')
    product_tmpl_id = fields.Many2one(
        'product.template', 'Product', ondelete='cascade',
        help="Specify a template if this rule only applies to one product template. Keep empty otherwise.")
    comision = fields.Float(string='Comision', help="Porcentaje que se aplica al producto.", related="product_tmpl_id.comision", copy=False,readonly=False)
    tabla_comision_id = fields.Many2one('venta.comision.tabla', index=True, ondelete='cascade', required=True, string='Tabla de Comision')

    def unlink(self):
        for record in self:
            contexto = self.env.context
            if not 'tracking' in contexto:
                record.tabla_comision_id.message_post(body=_("Se elimino el producto de las excepciones %s") % (record.product_tmpl_id.name))
        super(VentaTablaComisionProducto, self).unlink()
    
    @api.model_create_multi
    def create(self, vals_list):
        contexto = self.env.context
        print(contexto)
        print(vals_list)
        res_ids = super(VentaTablaComisionProducto, self).create(vals_list)
        for record in res_ids:
            if not 'tracking' in contexto:
                record.tabla_comision_id.message_post(body=_("Se agrego el producto : %s con comision: %s") % (record.product_tmpl_id.name, record.comision))
        return res_ids
    
    

class ProductTemplate(models.Model):
    _inherit = "product.template"

    comision = fields.Float(string='Comision', help="Porcentaje que se aplica al producto.",tracking=True)
    name = fields.Char('Name', index=True, required=True, translate=True,tracking=True)
    description = fields.Html(
        'Description', translate=True,tracking=True)
    description_purchase = fields.Text(
        'Purchase Description', translate=True,tracking=True)
    description_sale = fields.Text(
        'Sales Description', translate=True,
        help="A description of the Product that you want to communicate to your customers. "
             "This description will be copied to every Sales Order, Delivery Order and Customer Invoice/Credit Note",tracking=True)

    @api.onchange('comision')
    def _onchange_comision(self):
        if self.comision and self.comision < 0 or self.comision > 100:
            raise UserError(_('El porcentaje de comisión debe estar entre 0 y 100'))
        tabla_comision_producto = self.env['venta.comision.tabla.producto'].search([('product_tmpl_id','=',self._origin.id)])
        if tabla_comision_producto:
            tabla_comision_producto.tabla_comision_id.message_post(body=_('Comision: %s <span class="fa fa-long-arrow-right"/> %s') % (self._origin.comision,self.comision))

    
    def depuracion(self):
        p_bom = self.env['mrp.production'].search([])
        pp_bom = self.env['mrp.bom'].search([])        
        id_product = [pi.product_id.product_tmpl_id.id for pi in p_bom]
        id_product += pp_bom.ids
        product_template = self.env['product.template'].search([('id','not in',id_product)])
        depurar = []
        for product in product_template:
            producto = self.env['product.template'].search([('name','=',product.name)])
            if len(producto) > 1:
                p = self.env['product.product'].search([('product_tmpl_id','in',producto.ids)])
                acm = self.env['account.move.line'].search([('product_id','in',p.ids)])
                sm = self.env['stock.move'].search([('product_id','in',p.ids)])
                if len(acm) == 0 and len(sm) == 0:
                    depurar.append(p[0].id)
                    
        eliminar = self.env['product.product'].search([('id','in',depurar)])
        eliminar.unlink()
        return True
