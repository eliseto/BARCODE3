# -*- coding: utf-8 -*-
from datetime import date, datetime, timedelta
from odoo import models, fields, exceptions, api, _
from odoo.exceptions import UserError
import logging

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def get_moneda(self,monto):
        for rec in self:
            if rec.country_id and rec.country_id.id == 90:
                return '{}.{:,.2f}'.format('Q',monto)
            else:
                return '{}.{:,.2f}'.format('$',monto)


    def get_info_credit(self):
        documentos = []
        for rec in self:
            invoice_ids = rec.invoice_ids.filtered(lambda x : x.move_type == 'out_invoice' and x.state == 'posted' and x.journal_id.tipo_documento and x.journal_id.tipo_documento in ['FACT','FCAM']).sorted(key=lambda r: r.invoice_date)
            total_abono = total_cargo = 0
            for inv in invoice_ids:
                partner = inv.partner_id
                pais = partner.country_id.id if partner.country_id else False
                moneda_reporte = inv.company_id.currency_id.symbol if pais and pais != 90 else '$'
                total_documentos = []
                total_documentos.append(inv)
                #buscar notas de debito aplicadas al documento
                nd = self.env['account.move'].sudo().search([('fel_factura_referencia_id','=',inv.id)])
                if nd:
                    total_documentos.append(nd)
                for invoice in total_documentos:
                    aplicaciones = invoice._get_reconciled_info_JSON_values()
                    saldo_factura = invoice.amount_total if pais and pais != 90 else invoice.amount_total_signed
                    total_cargo += saldo_factura
                    
                    factura = {
                        'documento': dict(invoice.journal_id._fields['tipo_documento'].selection).get(invoice.journal_id.tipo_documento) if invoice.journal_id.tipo_documento else ''
                        ,'numero':invoice.name
                        ,'emision':invoice.invoice_date
                        ,'vencimiento':invoice.invoice_date_due
                        ,'plazo':invoice.invoice_payment_term_id.name if invoice.invoice_payment_term_id else 'Contado'
                        ,'transcurrido':(date.today() - invoice.invoice_date).days
                        ,'retraso':self.dias_atraso(invoice)
                        ,'abono_m':0
                        ,'cargo_m':invoice.amount_total_signed if pais and pais == 90 else invoice.amount_total
                        ,'cargo':'{}.{:,.2f}'.format(invoice.company_id.currency_id.symbol,invoice.amount_total_signed) if pais and pais == 90 else '{}.{:,.2f}'.format(invoice.currency_id.symbol,invoice.amount_total)
                        ,'abono':''
                        ,'saldo':'{}.{:,.2f}'.format(invoice.company_id.currency_id.symbol,invoice.amount_total_signed) if pais and pais == 90 else '{}.{:,.2f}'.format(invoice.currency_id.symbol,invoice.amount_total)}
                    pagos = []
                    if aplicaciones:
                        payment = lambda id : self.env['account.payment'].sudo().search([('id','=',id)])
                        move_id = lambda id : self.env['account.move'].sudo().search([('id','=',id)])
                        move_pay = lambda id : self.env['account.move'].sudo().search([('payment_id','=',id)])
                        doc = doc_name = fecha = abono = ''
                        for aplicacion in aplicaciones:
                            if aplicacion['account_payment_id']:
                                pago = payment(aplicacion['account_payment_id']) if pais and pais != 90 else move_pay(aplicacion['account_payment_id'])
                                doc = aplicacion['journal_name']
                                doc_name = pago.name
                                fecha = aplicacion['date']
                                abono = aplicacion['amount'] if pais and pais != 90 else pago.amount_total_signed
                                moneda = pago.currency_id.symbol if pais and pais != 90 else pago.company_id.currency_id.symbol
                            else:
                                move = move_id(aplicacion['move_id'])
                                doc = dict(move.journal_id._fields['tipo_documento'].selection).get(move.journal_id.tipo_documento) if move.journal_id.tipo_documento else ''
                                doc_name = move.name
                                fecha = aplicacion['date']
                                abono = abs(move.amount_total_signed) if pais and pais == 90 else abs(move.amount_total)
                                moneda = move.company_id.currency_id.symbol if pais and pais == 90 else invoice.currency_id.symbol
                            saldo_factura -= abono
                            saldo_factura = abs(saldo_factura)
                            total_abono += abono


                            pagos.append({
                                'documento': doc
                                ,'numero': doc_name
                                ,'emision': fecha
                                ,'vencimiento':''
                                ,'plazo':''
                                ,'transcurrido':''
                                ,'retraso':''
                                ,'cargo_m':0
                                ,'abono_m':abono
                                ,'cargo':''
                                ,'abono': '{}.{:,.2f}'.format(moneda,abono)
                                ,'saldo':'{}.{:,.2f}'.format(moneda,saldo_factura)})


                            if invoice.amount_residual == 0:
                                factura['transcurrido'] = abs((factura['emision'] - fecha).days)
                                if fecha > factura['vencimiento']:
                                    factura['retraso'] = (fecha - factura['vencimiento']).days
                    documentos.append(factura)
                    if pagos:
                        documentos.extend(pagos)
                #agregar linea en blanco
                documentos.append({'documento':'','numero':'','emision':'','vencimiento':'','plazo':'','transcurrido':'','retraso':'','cargo':'','abono':'','saldo':'','abono_m':0,'cargo_m':0})
        return documentos
        

    def dias_atraso(self,invoice):
        if invoice.invoice_date_due < date.today():
            return (date.today() - invoice.invoice_date_due).days
        else:
            return 0



