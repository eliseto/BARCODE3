# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError

class AccoutMoveComision(models.Model):
    _inherit = "account.move"

    venta_comision_id = fields.Many2one('venta.comision', string="Commision",)

    def get_pagos_aplicados_factura(self):
        #Devuelve los pagos que fueron aplicados a esta factura
        query = """
            SELECT ml2.id, m2.date, apr.amount
            FROM account_move_line ml
            JOIN account_partial_reconcile apr on apr.debit_move_id = ml.id
            JOIN account_move_line ml2 on apr.credit_move_id = ml2.id
            JOIN account_move m2 on ml2.move_id = m2.id
            where (select internal_type from account_account where id = ml.account_id) = 'receivable'
            and ml.move_id = %s
            order by m2.date
        """
        self._cr.execute(query, (self.id,))
        pagos = []
        print("self.id-->",self.id)
        for r in self._cr.fetchall():
            pago = {
            'id': r[0],
            'fecha': r[1],
            'monto': r[2],
            }
            pagos.append(pago)

        return pagos

    def get_factura_aplicados_pagos(self,id):
        #Devuelve los pagos que fueron aplicados a esta factura
        query = """
            SELECT ml2.id,ml2.move_id payment_id,ml.move_id invoice_id, m2.date, apr.amount
            FROM account_move_line ml
            JOIN account_partial_reconcile apr on apr.debit_move_id = ml.id
            JOIN account_move_line ml2 on apr.credit_move_id = ml2.id
            JOIN account_move m2 on ml2.move_id = m2.id
            where (select internal_type from account_account where id = ml.account_id) = 'receivable'
            and ml2.move_id=%s
            limit 1
        """
        self._cr.execute(query, (id,))
        pagos = []
        for r in self._cr.fetchall():
            pago = {
            'id': r[0],
            'payment_id': r[1],
            'invoice_id': r[2],
            'date': r[3],
            'amount': r[4],
            }
            pagos.append(pago)

        return pagos    

class AccoutMoveComision(models.Model):
    _inherit = "account.move.line"

    costo = fields.Float(compute='_product_margin', digits='Product Price', store=True)

    @api.depends('product_id', 'quantity', 'price_unit', 'price_subtotal')
    def _product_margin(self):
        for line in self:
            if line.product_id:
                currency = line.currency_id
                costo = line.product_id.standard_price * line.quantity
                line.costo = currency.round(costo) if currency else costo
