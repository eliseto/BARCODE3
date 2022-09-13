from odoo import fields, models, api
import logging

_logger = logging.getLogger( __name__ )

class ProductProduct(models.Model):
    _inherit = 'product.product'
    old_cost = fields.Float(string="Ultimo Costo")


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    old_cost = fields.Float(related="product_variant_id.old_cost", string="Ultimo costo")


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        for rec in self:
            if rec.purchase_id.order_line:
                for line in rec.purchase_id.order_line:
                    # Convert currency
                    if rec.company_id.currency_id!=line.currency_id:
                        if rec.manual_currency_exchange_rate:
                            price = (line.price_subtotal/line.product_qty)/(1/rec.manual_currency_exchange_rate)
                        else:
                            price = line.currency_id._convert(
                                from_amount=(line.price_subtotal/line.product_qty), 
                                to_currency=rec.company_id.currency_id,
                                company=line.company_id,
                                date=line.date_planned
                            )
                        line.product_id.old_cost = price
                    else:
                        line.product_id.old_cost =(line.price_subtotal/line.product_qty)
        return res