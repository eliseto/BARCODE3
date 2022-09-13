
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
import logging

from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp
from odoo.addons.stock_landed_costs.models import product
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class Stock_Landed_Cost_Line(models.Model):
    _inherit = 'stock.landed.cost.lines'

    amount_currency = fields.Monetary(string='Importe en moneda', store=True, copy=True,
        help="The amount expressed in an optional other currency if it is a multi-currency entry.")
    
    @api.onchange('amount_currency')
    def _onchange_amount_currency(self):
        for line in self:
            line.price_unit = round(line.amount_currency * line.cost_id.tasa_cambio,2)

class stock_landed_cost(models.Model):
    _inherit = 'stock.landed.cost'

    aranceles_ids = fields.One2many('stock.valuation.arancel', 'cost_id', string='Aranceles')
    tasa_cambio = fields.Float(string='Tasa de Cambio', default=1.0,digits=(2, 8),readonly=False, states={'done': [('readonly', True)]})
    tc_currency_id = fields.Many2one('res.currency', string='Moneda', default=lambda self: self.env.user.company_id.currency_id, required=True, readonly=False, states={'done': [('readonly', True)]})
    
    @api.onchange('tasa_cambio','tc_currency_id')
    def _onchange_amount_currency(self):
        for cost in self:
            if cost.cost_lines:
                for line in cost.cost_lines:
                    line.price_unit = line.amount_currency * cost.tasa_cambio

    def get_valuation_lines(self):
        lines = []

        for move in self.mapped('picking_ids').mapped('move_lines').mapped('stock_valuation_layer_ids'):
            # it doesn't make sense to make a landed cost for a product that isn't set as being valuated in real time at real cost
            if move.product_id.valuation != 'real_time' or move.product_id.cost_method not in ['average','fifo']:
                continue
            vals = {
                'product_id': move.product_id.id,
                'move_id': move.stock_move_id.id,
                'stock_valuation_layer_id': move.id,
                'quantity': move.quantity,
                'former_cost': move.value,
                'weight': move.product_id.weight * move.quantity,
                'volume': move.product_id.volume * move.quantity
            }
            lines.append(vals)

        if not lines and self.mapped('picking_ids'):
            raise UserError(_("You cannot apply landed costs on the chosen transfer(s). Landed costs can only be applied for products with automated inventory valuation and FIFO costing method."))
        return lines
        

    
    def button_validate(self):
        if any(cost.state != 'draft' for cost in self):
            raise UserError(_('Only draft landed costs can be validated'))
        if any(not cost.valuation_adjustment_lines for cost in self):
            raise UserError(_('No valuation adjustments lines. You should maybe recompute the landed costs.'))
        print(self._check_sum())
        if not self._check_sum():
            raise UserError(_('Cost and adjustments lines do not match. You should maybe recompute the landed costs.'))

        for cost in self:
            move = self.env['account.move']
            move_vals = {
                'journal_id': cost.account_journal_id.id,
                'date': cost.date,
                'ref': cost.name,
                'line_ids': [],
            }
            #amount_arancel = 0.00
            #for item in cost.aranceles_ids.filtered(lambda line: line.move_id):
            for line in cost.valuation_adjustment_lines.filtered(lambda line: line.move_id):
                #print("-------------Nombre producto-------------")
                #print(line.product_id.name)
                stock_valuation_layer_id = line.move_id.stock_valuation_layer_ids[0]
                if line.product_id.categ_id.property_cost_method == 'average' and line.product_id.qty_available > 0:
                    adjust_value = line.additional_landed_cost 
                    qty_available = line.product_id.qty_available
                    standard_price = line.product_id.standard_price
                    pro_price = (adjust_value + (qty_available * standard_price)) / qty_available
                    line.product_id.write({'standard_price':pro_price})
                # Prorate the value at what's still in stock
                cost_to_add = (stock_valuation_layer_id.remaining_qty / stock_valuation_layer_id.quantity) * line.additional_landed_cost

                new_landed_cost_value = line.final_cost + line.additional_landed_cost
                line.move_id.write({
                    #'landed_cost_value': new_landed_cost_value,
                    'price_unit': (stock_valuation_layer_id.value + line.additional_landed_cost) / stock_valuation_layer_id.quantity,
                })
                stock_valuation_layer_id.write({
                    'value': stock_valuation_layer_id.value + line.additional_landed_cost,
                    'remaining_value': stock_valuation_layer_id.remaining_value + cost_to_add,
                })
                # `remaining_qty` is negative if the move is out and delivered proudcts that were not
                # in stock.
                qty_out = 0
                if line.move_id._is_in():
                    qty_out = stock_valuation_layer_id.quantity - stock_valuation_layer_id.remaining_qty
                elif line.move_id._is_out():
                    qty_out = stock_valuation_layer_id.quantity
                move_vals['line_ids'] += line._create_accounting_entries(move, qty_out)

            move = move.create(move_vals)
            cost.write({'state': 'done', 'account_move_id': move.id})
            move.post()
        return True
    
    def compute_landed_cost(self):
        AdjustementLines = self.env['stock.valuation.adjustment.lines']
        AdjustementLines.search([('cost_id', 'in', self.ids)]).unlink()

        digits = 2#dp.get_precision('Product Price')
        _logger.info( digits )
        towrite_dict = {}
        for cost in self.filtered(lambda cost: cost.picking_ids):
            total_qty = 0.0
            total_cost = 0.0
            total_weight = 0.0
            total_volume = 0.0
            total_line = 0.0
            all_val_line_values = cost.get_valuation_lines()
            for val_line_values in all_val_line_values:
                val_line_values.update({'cost_id': cost.id})
                self.env['stock.valuation.arancel'].create(val_line_values)
                for cost_line in cost.cost_lines:
                    val_line_values.update({'cost_line_id': cost_line.id})
                    self.env['stock.valuation.adjustment.lines'].create(val_line_values)
                total_qty += val_line_values.get('quantity', 0.0)
                total_weight += val_line_values.get('weight', 0.0)
                total_volume += val_line_values.get('volume', 0.0)

                former_cost = val_line_values.get('former_cost', 0.0)
                # round this because former_cost on the valuation lines is also rounded
                total_cost += tools.float_round(former_cost, precision_digits=digits) if digits else former_cost

                total_line += 1

            for line in cost.cost_lines:
                value_split = 0.0
                for valuation in cost.valuation_adjustment_lines:
                    value = 0.0
                    if valuation.cost_line_id and valuation.cost_line_id.id == line.id:
                        if line.split_method == 'by_quantity' and total_qty:
                            per_unit = (line.price_unit / total_qty)
                            value = valuation.quantity * per_unit
                        elif line.split_method == 'by_weight' and total_weight:
                            per_unit = (line.price_unit / total_weight)
                            value = valuation.weight * per_unit
                        elif line.split_method == 'by_volume' and total_volume:
                            per_unit = (line.price_unit / total_volume)
                            value = valuation.volume * per_unit
                        elif line.split_method == 'equal':
                            value = (line.price_unit / total_line)
                        elif line.split_method == 'by_current_cost_price' and total_cost:
                            per_unit = (line.price_unit / total_cost)
                            value = valuation.former_cost * per_unit
                        else:
                            value = (line.price_unit / total_line)

                        if digits:
                            value = tools.float_round(value, precision_digits=digits, rounding_method='UP')
                            fnc = min if line.price_unit > 0 else max
                            value = fnc(value, line.price_unit - value_split)
                            value_split += value

                        if valuation.id not in towrite_dict:
                            towrite_dict[valuation.id] = value
                        else:
                            towrite_dict[valuation.id] += value
        for key, value in towrite_dict.items():
            AdjustementLines.browse(key).write({'additional_landed_cost': value})
        return True

    #
    #def get_arancel(models, product_id=None, move_id=None):
    #    if product_id and move_id:
            
class StockValuationArancel(models.Model):
    _name = 'stock.valuation.arancel'
    _description = 'Stock Valuation Arancel'

    name = fields.Char(
        'Description', compute='_compute_name', store=True)
    cost_id = fields.Many2one(
        'stock.landed.cost', 'Landed Cost',
        ondelete='cascade', required=True)
    move_id = fields.Many2one('stock.move', 'Stock Move', readonly=True)
    stock_valuation_layer_id = fields.Many2one('stock.valuation.layer', 'Stock Valuation Layer', readonly=True)
    product_id = fields.Many2one('product.product', 'Producto', required=True)
    quantity = fields.Float('Cantidad', default=1.0, digits=0, required=True)
    weight = fields.Float('Peso', default=1.0)
    volume = fields.Float('Volumen', default=1.0)
    former_cost = fields.Float('FOB')
    additional_landed_cost = fields.Float('Additional Landed Cost')
    currency_id = fields.Many2one('res.currency', related='cost_id.company_id.currency_id')
    arancel_id = fields.Many2one('arancel.type', related='product_id.arancel_id', string='Arancel %')
    arancel_amount = fields.Float('Aranceles', compute="_compute_aranceles")
    

    @api.depends(
        'product_id',
        'former_cost',
        'quantity',
        'arancel_id',
    )
    def _compute_aranceles(self):
        for rec in self:
            rec.update({
                'arancel_amount': ((rec.former_cost * rec.arancel_id.amount_arancel if rec.arancel_id else 0.00) / 100) or 0.00,
            })

class StockValuationAdjustmentLines(models.Model):
    _inherit = 'stock.valuation.adjustment.lines'
    
    stock_valuation_layer_id = fields.Many2one('stock.valuation.layer', 'Stock Valuation Layer', readonly=True)