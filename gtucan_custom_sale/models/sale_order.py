# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def get_simple_name(self):
        if self.product_id:
            if self.default_code:
                default_code = '[code]'.format(self.default_code)
                product_name = self.name.replace(default_code, '')
                return product_name
        return self.name

class ProductPriceList(models.Model):
    _inherit = 'product.pricelist'

    def delete_pricelist_item(self):
        for record in self:
            for item in record.item_ids:
                item.unlink()

class SaleOrder(models.Model):
    _inherit='sale.order'