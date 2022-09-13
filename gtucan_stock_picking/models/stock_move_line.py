# -*- coding: utf-8 -*-

from odoo import _, api, fields, models

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"
    _order = 'stock_order asc'

    stock_order = fields.Integer(related='location_id.stock_order',store=True)