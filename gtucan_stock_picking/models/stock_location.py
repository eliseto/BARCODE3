
from odoo import _, api, fields, models

class Location(models.Model):
    _inherit = 'stock.location'

    stock_order = fields.Integer(string="Orden", readonly=False, required=True, copy=False, default=99999)

    @api.model
    def create(self, vals):
        if vals.get('stock_order', 99999) == 99999:
            vals['stock_order'] = self.env['ir.sequence'].next_by_code(
                'stock.location.order') or 99999
        result = super(Location, self).create(vals)
        return result