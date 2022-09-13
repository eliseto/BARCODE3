# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class AccountMove(models.Model):
    _inherit = "account.move"

    no_linea = fields.Integer('Numero de Linea', compute='_compute_no_linea')

    sat_importa_in_ca = fields.Monetary(string="Importacion In CA", compute='_compute_libro_fiscal')
    sat_importa_out_ca = fields.Monetary(string="Importacion Out CA", compute='_compute_libro_fiscal')

    sat_exportacion_in_ca = fields.Monetary(string="Exportacion In CA", compute='_compute_libro_fiscal')
    sat_exportacion_out_ca = fields.Monetary(string="Exportacion Out CA", compute='_compute_libro_fiscal')

    sat_servicio = fields.Monetary(string="Servicio", compute='_compute_libro_fiscal', currency_field='company_currency_id')
    sat_bien = fields.Monetary(string="Bien", compute='_compute_libro_fiscal', currency_field='company_currency_id')
    sat_exento = fields.Monetary(string="Exento", compute='_compute_libro_fiscal', currency_field='company_currency_id')
    sat_peq_contri = fields.Monetary(string="Pequeño Contribuyente", compute='_compute_libro_fiscal', currency_field='company_currency_id')
    sat_iva = fields.Monetary(string="IVA", compute='_compute_libro_fiscal', currency_field='company_currency_id')
    sat_iva_porcentaje = fields.Float(string="IVA Porcentaje", compute='_compute_libro_fiscal')
    sat_subtotal = fields.Monetary(string="Subtotal", compute='_compute_libro_fiscal', currency_field='company_currency_id')
    sat_amount_total = fields.Monetary(string="Sat Total", compute='_compute_libro_fiscal', currency_field='company_currency_id')
    sat_combustible = fields.Monetary(string="Combustible", compute='_compute_libro_fiscal', currency_field='company_currency_id')
    sat_base = fields.Monetary(string="Base", compute='_compute_libro_fiscal', currency_field='company_currency_id')


    sat_valor_transaccion = fields.Float(string="Valor de transaccion", digits=(8, 2), readonly=True, states={'draft': [('readonly', False)]},)
    sat_gastos_transporte = fields.Float(string="Gastos de Transporte", digits=(8, 2), readonly=True, states={'draft': [('readonly', False)]},)
    sat_gastos_seguros = fields.Float(string="Gastos de Seguro", digits=(8, 2), readonly=True, states={'draft': [('readonly', False)]},)
    sat_gastos_otros = fields.Float(string="Otros Gastos", digits=(8, 2), readonly=True, states={'draft': [('readonly', False)]},)
    sat_tasa_cambio = fields.Float(string="Tasa de cambio", digits=(8, 5), readonly=True, states={'draft': [('readonly', False)]},)

    sat_invoice_id = fields.Many2one('account.move', string='Factura Relacionada')
    sat_invoice_name = fields.Char(related='sat_invoice_id.name', readonly=True, string='Invoice name')
    sat_invoice_child_ids = fields.One2many('account.move', 'sat_invoice_id', string='Invoice Links', domain=[('state', '=', 'posted')], readonly=True, states={'draft': [('readonly', False)]})
    fel_factura_referencia_id = fields.Many2one('account.move', string="Factura Referencia", help="Factura de referencia para ligar la nota de debito con la factura",
                                    domain="[('company_id', '=', company_id),('state', '=', 'posted'),('move_type', '=', 'out_invoice'),('partner_id', '=', partner_id)]",)

    #Estoy trabajando en solo linkiar los documentos y no utilizarlos para la carga


    fac_numero = fields.Char('Numero', copy=False, readonly=True, states={'draft': [('readonly', False)]},)
    fac_serie = fields.Char('Serie', copy=False, readonly=True, states={'draft': [('readonly', False)]},)

    sat_fac_numero = fields.Char(string="Numero Factura", compute='_compute_libro_fiscal')
    sat_fac_serie = fields.Char(string="Serie Factura", compute='_compute_libro_fiscal')

    journal_tipo_operacion = fields.Selection(related='journal_id.tipo_operacion', readonly=True)

    referencia_interna = fields.Char(string="Referencia Interna", compute='_referencia_interna')

    def _referencia_interna(self):
        largo = 25
        for d in self:
            if d.ref:
                if len(d.ref) > largo:
                    d.referencia_interna = d.ref[0:largo]
                else:
                    d.referencia_interna = d.ref
            else:
                d.referencia_interna = ''

    def _compute_no_linea(self):
        self.no_linea = 0

    def linea_blanco(self, contador):
        linea_blanco = {
            'linea': contador,
            'blanco': True,
        }
        return linea_blanco

    def nueva_linea(self, cadena, largo_lineas):
        largo = largo_lineas
        nueva_desc = []

        while True:
            if len(cadena) > largo:
                nueva_cadena = cadena[0:largo]
                x = nueva_cadena.rfind(' ')
                #El siguiente codigo es para validar si no existe un espacion que encontrar entonces lo corta por el largo
                if x < 0:
                    x = largo
                nueva_cadena = cadena[0:x]
                nueva_desc.append(nueva_cadena)
                cadena = cadena[x+1:len(cadena)]
            else:
                nueva_desc.append(cadena)
                break
        return nueva_desc

    @api.depends(
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state')
    def _compute_libro_fiscal(self):
        invoice_ids = [move.id for move in self if move.id and move.is_invoice(include_receipts=True)]

        for move in self:
            move.sat_iva_porcentaje = 0
            total_untaxed = 0.0
            total_untaxed_currency = 0.0
            total_tax = 0.0
            total_tax_currency = 0.0
            total_residual = 0.0
            total_residual_currency = 0.0
            total = 0.0
            total_currency = 0.0
            iva_importacion = 0.0
            iva = 0.0
            currencies = set()

            total_servicio = total_servicio_iva = 0.0
            total_bien = total_bien_iva = 0.0
            sat_peq_contri = sat_exento = sat_combustible = 0.0
            sat_importa_in_ca = 0

            sat_exportacion_in_ca = sat_exportacion_out_ca = 0

            if move.fac_serie:
                move.sat_fac_serie = move.fac_serie
            else:
                if move.name:
                    move.sat_fac_serie = move.name[move.name.rfind("/")+1:move.name.find("-")]

            if move.fac_numero:
                move.sat_fac_numero = move.fac_numero
            else:
                if move.name:
                    move.sat_fac_numero = move.name[move.name.find("-")+1:len(move.name)]

            for line in move.line_ids:
                if line.currency_id:
                    currencies.add(line.currency_id)

                if move.is_invoice(include_receipts=True):
                    # === Invoices ===

                    if not line.exclude_from_invoice_tab:
                        # Untaxed amount.
                        total_untaxed += line.balance
                        total_untaxed_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.tax_line_id:
                        # Tax amount.
                        total_tax += line.balance
                        total_tax_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.account_id.user_type_id.type in ('receivable', 'payable'):
                        # Residual amount.
                        total_residual += line.amount_residual
                        total_residual_currency += line.amount_residual_currency
                else:
                    # === Miscellaneous journal entry ===
                    if line.debit:
                        total += line.balance
                        total_currency += line.amount_currency

                for impuesto in line.tax_line_id:
                    if impuesto.impuesto_sat == 'ipeq':
                        sat_peq_contri += line.balance
                    elif impuesto.impuesto_sat == 'iva':
                        move.sat_iva_porcentaje = impuesto.amount
                        iva += line.balance
                    elif impuesto.impuesto_sat in ('idp','itme'):
                        sat_exento += line.balance
                    elif impuesto.impuesto_sat == 'inguat':
                        sat_exento += line.balance
                #Cuando una factura en este caso ventas tiene iva exento, entonces no tiene tax_line_id, por esa razon se debe de ir a los tax_ids.
                es_exento = False
                if not line.tax_line_id:
                    for taxids in line.tax_ids:
                        if taxids.impuesto_sat == 'exeiva':
                            es_exento = True
                            sat_exento += line.balance


                if line.product_id and not es_exento:
                    if move.journal_id.tipo_documento == 'FPEQ':
                        sat_peq_contri += line.balance
                    elif line.product_id.sat_tipo_producto == 'gas':
                        sat_combustible += line.balance
                    elif line.product_id.sat_tipo_producto == 'exento':
                        sat_exento += line.balance
                    elif line.product_id.sat_tipo_producto == 'exp_in_ca_bien':
                        sat_exportacion_in_ca += line.balance
                    elif line.product_id.sat_tipo_producto == 'imp_out_ca_bien':
                        iva_importacion += line.balance
                    elif line.product_id.type in ('service'):
                        total_servicio += line.balance
                    else:
                        total_bien += line.balance


            if move.move_type == 'out_invoice':
                sign = -1
            elif move.move_type == 'out_refund':
                sign = -1
            else:
                sign = 1
            #move.amount_untaxed = sign * (total_untaxed_currency if len(currencies) == 1 else total_untaxed)
            #move.amount_tax = sign * (total_tax_currency if len(currencies) == 1 else total_tax)
            #move.amount_total = sign * (total_currency if len(currencies) == 1 else total)
            #move.amount_residual = -sign * (total_residual_currency if len(currencies) == 1 else total_residual)
            #move.amount_untaxed_signed = -total_untaxed
            #move.amount_tax_signed = -total_tax
            #move.amount_total_signed = abs(total) if move.move_type == 'entry' else -total
            #move.amount_residual_signed = total_residual
            move.sat_exento = 0
            move.sat_servicio = 0
            move.sat_bien = 0
            move.sat_iva = 0
            move.sat_subtotal = 0
            move.sat_amount_total = 0
            move.sat_peq_contri = 0
            move.sat_combustible = 0
            move.sat_base = 0
            move.sat_importa_in_ca = 0
            move.sat_importa_out_ca = 0
            move.sat_exportacion_in_ca = 0

            if move.state == 'cancel':
                move.sat_exento = 0

            elif move.journal_id.tipo_operacion == 'DUCA_IN':
                move.sat_iva = iva_importacion
                move.sat_importa_in_ca = move.sat_iva / 0.12
                move.sat_exportacion_in_ca = sign * sat_exportacion_in_ca
                move.sat_exento = sign * sat_exento
                move.sat_amount_total = move.sat_importa_in_ca + move.sat_iva + move.sat_exportacion_in_ca + move.sat_exento

            elif move.journal_id.tipo_operacion == 'DUCA_OUT':
                move.sat_iva = iva_importacion
                move.sat_importa_out_ca = move.sat_iva / 0.12
                move.sat_exento = sign * sat_exento
                move.sat_amount_total = move.sat_importa_out_ca + move.sat_iva + move.sat_exento

            else:

                move.sat_servicio = sign * total_servicio
                move.sat_bien = sign * total_bien
                move.sat_exento = sign * sat_exento
                move.sat_combustible = sign * sat_combustible
                move.sat_iva = sign * iva
                move.sat_subtotal = move.sat_servicio + move.sat_bien



                move.sat_peq_contri = sat_peq_contri
                move.sat_amount_total = move.sat_subtotal + move.sat_iva + move.sat_exento + move.sat_combustible + move.sat_peq_contri
                move.sat_base = move.sat_servicio + move.sat_bien + move.sat_combustible

            currency = len(currencies) == 1 and currencies.pop() or move.company_id.currency_id
            is_paid = currency and currency.is_zero(move.amount_residual) or not move.amount_residual
