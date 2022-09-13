# -*- coding: utf-8 -*-
# Copyright 2022 Alonso Nuñez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    vendor_related_invoice_ids = fields.Many2many('account.move', string="Related Invoices", domain=[('move_type', '=', 'in_invoice')], states={'done': [('readonly', True)]})

    def button_validate(self):
        res = super(StockLandedCost, self).button_validate()
        for rec in self:
            if rec.picking_ids:
                for picking in rec.picking_ids:
                    if rec.valuation_adjustment_lines:
                        total = sum([(adj.former_cost/adj.quantity) for adj in rec.valuation_adjustment_lines])
                        if picking.purchase_id:
                            for line in picking.purchase_id.order_line:
                                if rec.company_id.currency_id!=rec.currency_id:
                                    if rec.tasa_cambio:
                                        price = (line.price_subtotal/line.product_qty)/(1/rec.tasa_cambio)
                                    else:
                                        price = rec.currency_id._convert(
                                            from_amount=total, 
                                            to_currency=rec.company_id.currency_id,
                                            company=rec.company_id,
                                            date=rec.date
                                        )
                                    line.product_id.old_cost = line.product_id.old_cost + price
                                else:
                                    line.product_id.old_cost = line.product_id.old_cost + total
        return res