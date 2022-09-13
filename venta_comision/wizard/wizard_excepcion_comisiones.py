# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
import base64
import tempfile
import binascii
import xlrd
from datetime import datetime,timedelta

class VentaComisionLine(models.TransientModel):
    _name = "wizard.excepcion.comisiones"
    _description = "Wizard excepcion comisiones"
    name = fields.Char(string="Nombre")
    excepciones_file = fields.Binary(string='Excepciones', help="Archivo de excepciones para la tabla de comisiones")
    excepciones_name = fields.Char(string='Excepciones XLSX', help="Nombre de archivo de excepciones para la tabla de comisiones")

    """
    Al momento de cargar el archivo con las excepciones, se debe contemplar lo siguiente:
    1. Almacenar de manera temporal todos los productos actuales con excepcion.
    2. Borrar todas las excepciones actuales.
    3. Realizar una carga masiva de las excepciones.
    4. Validar que excepciones sufrieron cambios.
    5. Si se eliminaron excepciones, almenarlas en una lista para mostrar esto en el tracking.
    6. Si se agregaron excepciones, almenarlas en una lista para mostrar esto en el tracking.
    """
    def load_exception(self):
        if not self.excepciones_file:
            raise UserError(_('Debe cargar un archivo con las excepciones.'))
        contexto = self.env.context
        tabla_comisiones = self.env[contexto['active_model']].search([('id', '=', contexto['active_id'])])
        try:
            fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
            fp.write(binascii.a2b_base64(self.excepciones_file))
            fp.seek(0)
            vals = {}
            workbook = xlrd.open_workbook(fp.name)
            sheet = workbook.sheet_by_index(0)
            nuevas_excepciones = []
            actualizacion_excepciones = []
            for i in range(sheet.nrows):
                if i == 0:
                    continue
                row = sheet.row_values(i)
                if row[0] == '':
                    continue
                product_template = self.env['product.template'].search([('default_code', '=', row[0]),('name', '=', row[1])])
                if product_template:
                    if not tabla_comisiones.producto_ids.search([('product_tmpl_id','=',product_template.id)]):
                        tabla_comisiones.producto_ids.with_context({'tracking':False}).create({'product_tmpl_id': product_template.id, 'name': product_template.name, 'tabla_comision_id': tabla_comisiones.id})
                    product_template.write({'comision': row[2]})
            attachments = [(self.excepciones_name, self.excepciones_file)]
            msg = 'Se cargaron las excepciones desde el wizard masivamente'
            tabla_comisiones.message_post(subject='Excepciones cargadas: ', body=msg ,attachments=attachments)
        except Exception as e:
            raise UserError(_("Error al cargar archivo: %s") % str(e))
    
    def delete_exception(self):
        contexto = self.env.context
        tabla_comisiones = self.env[contexto['active_model']].search([('id', '=', contexto['active_id'])])
        productos_eliminados = []
        msg = 'Se eliminaron toda las excepciones desde el wizard masivamente'
        tabla_comisiones.message_post(subject='Limpieza de excepciones', body=msg)
        tabla_comisiones.producto_ids.with_context({'tracking':False}).unlink()

    def load_invoice(self):
        if not self.excepciones_file:
            raise UserError(_('Debe cargar un archivo con las excepciones.'))
        contexto = self.env.context
        try:
            journal_id = self.env['account.journal'].search([('name', '=', 'Efectivo - Caja 1')], limit=1)
            extracto = self.env['account.bank.statement'].create({'name': 'Junio Comisiones 2022', 'journal_id': journal_id.id, 'date': '2022-06-01'})
            s = [0,1,2]
            fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
            fp.write(binascii.a2b_base64(self.excepciones_file))
            fp.seek(0)
            vals = {}
            workbook = xlrd.open_workbook(fp.name)
            sheet_count = workbook.nsheets
            for x in range(sheet_count):
                venta = 0
                ventas = []
                sheet = workbook.sheet_by_index(x)
                nuevas_excepciones = []
                actualizacion_excepciones = []
                for i in range(sheet.nrows):
                    row = sheet.row_values(i)
                    if i == 0:
                        continue
                    elif row[0]:
                        account_move = self.env['account.move']
                        sale_order = self.env['sale.order']
                        partner_id = self.env['res.partner'].search([('name', '=', row[0])], limit=1)
                        partner_id.credit_limit = 10000000
                        comercial = partner_id.user_id.id if partner_id.user_id else False
                        #fecha = datetime(day=int(row[1])+1, month=6, year=2022)
                        fecha = xlrd.xldate.xldate_as_datetime(row[1], workbook.datemode)
                        fecha_vencimiento = xlrd.xldate.xldate_as_datetime(row[1], workbook.datemode)
                        fecha = fecha + timedelta(days=1)
                        fecha_vencimiento = fecha_vencimiento + timedelta(days=1)
                        plazo = partner_id.property_payment_term_id.id if partner_id.property_payment_term_id else False
                        venta = sale_order.create({
                            'partner_id': partner_id.id,
                            'date_order': fecha,
                            'user_id': comercial,
                            'payment_term_id': plazo,
                            #'validity_date': fecha_vencimiento,
                        })
                        cantidad_pagos = list(range(row.index('Pagos')+1,len(row)))
                        pagos = []
                        flag=1
                        for i in cantidad_pagos:
                            if flag & 1 == 0:
                                flag += 1

                            else:
                                fecha_pago = xlrd.xldate.xldate_as_datetime(row[i+1], workbook.datemode)
                                fecha_pago = fecha_pago + timedelta(days=1)
                                pagos.append([row[i], fecha_pago])
                                flag += 1
                                break
                                
                        ventas.append({'venta': venta, 'pagos': pagos})
                        account_move_line = self.env['account.move.line']
                    elif row[8] != '':
                        sale_order_line = self.env['sale.order.line']
                        product_template = self.env['product.template'].search([('name', '=', row[8])], limit=1)
                        product_template.write({'invoice_policy': 'order'})
                        product_id = self.env['product.product'].search([('product_tmpl_id', '=', product_template.id)], limit=1)
                        tax_id = self.env['account.tax'].search([('name', '=', 'IVA por Pagar')], limit=1)
                        sale_order_line.create({'order_id': venta.id, 'product_id': product_id.id, 'product_uom_qty': row[9], 'price_unit': row[10],'tax_id': [(6, 0, [tax_id.id])]})
                for v in ventas:
                    venta = v['venta']
                    list_pagos = v['pagos']
                    fecha_orden = venta.date_order
                    venta.action_confirm()
                    venta.date_order = fecha_orden
                    factura = venta._create_invoices()
                    factura.invoice_date = venta.date_order
                    factura.action_post()
                    account_bank_statement_line = self.env['account.bank.statement.line']
                    account_bank_statement_line.create({'statement_id': extracto.id, 'date': venta.date_order, 'payment_ref': factura.name, 'partner_id': factura.partner_id.id, 'amount': factura.amount_total})
                    for pagos in list_pagos:
                        fecha_pago = pagos[1]
                        monto = pagos[0]
                        pago = self.env['account.payment.register'].with_context(active_ids=factura.ids, active_model='account.move').create({
                            'payment_date': fecha_pago,
                            'journal_id': journal_id.id,
                        })._create_payments()
            extracto.balance_end_real = extracto.balance_end

        except Exception as e:
            raise UserError(_("Error al cargar archivo: %s") % str(e))