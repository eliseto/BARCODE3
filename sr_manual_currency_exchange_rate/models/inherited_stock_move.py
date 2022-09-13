# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_round
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    apply_manual_currency_exchange = fields.Boolean(string='Aplicar cambio de moneda manual')
    manual_currency_exchange_rate = fields.Float(string='Tasa de cambio de moneda manual')
    active_manual_currency_rate = fields.Boolean('active Manual Currency', default=False)
    active_validate_t_c = fields.Boolean(string='Validar TC', default=False)
    
    
    
    tc_status = fields.Selection([
        ('no','No'),
        ('passed', 'Aprobado'), 
        ('pending_aproval', 'Pendiente de Aprobar')],
        store=True, string="Estado de TC", compute='compute_validate_tc')
    
    @api.depends('active_validate_t_c')
    def compute_validate_tc(self):
        for rec in self:
            if rec.picking_type_id.id == 1:
                if rec.active_validate_t_c:
                    rec.tc_status = ('passed')
                else:
                    rec.tc_status = ('pending_aproval')
            else:
                rec.tc_status = ('no')    


    def button_validate(self):
        result = super(StockPicking,self).button_validate()
        for rec in self:
            if rec.picking_type_id.id == 1:
                if rec.apply_manual_currency_exchange:    
                    if not rec.active_validate_t_c:
                        raise UserError('¡ALERTA! no es posible procesar el ingreso, debido a que el tipo de cambio no ha sido validado')
        return result


class StockMove(models.Model):
    _inherit = 'stock.move'
    
    def _get_price_unit(self):
        """ Returns the unit price for the move"""
        self.ensure_one()
        if self.purchase_line_id and self.product_id.id == self.purchase_line_id.product_id.id:
            price_unit_prec = self.env['decimal.precision'].precision_get('Product Price')
            line = self.purchase_line_id
            order = line.order_id
            price_unit = line.price_unit
            if line.taxes_id:
                qty = line.product_qty or 1
                price_unit = line.taxes_id.with_context(round=False).compute_all(price_unit, currency=line.order_id.currency_id, quantity=qty)['total_void']
                price_unit = float_round(price_unit / qty, precision_digits=price_unit_prec)
            if line.product_uom.id != line.product_id.uom_id.id:
                price_unit *= line.product_uom.factor / line.product_id.uom_id.factor
            if self.picking_id and self.picking_id.active_manual_currency_rate and self.picking_id.apply_manual_currency_exchange:
                # The date must be today, and not the date of the move since the move move is still
                # in assigned state. However, the move date is the scheduled date until move is
                # done, then date of actual move processing. See:
                # https://github.com/odoo/odoo/blob/2f789b6863407e63f90b3a2d4cc3be09815f7002/addons/stock/models/stock_move.py#L36
                price_unit = price_unit / (1/self.picking_id.manual_currency_exchange_rate)
            else:
                price_unit = order.currency_id._convert(
                    price_unit, order.company_id.currency_id, order.company_id, fields.Date.context_today(self), round=False)
            return price_unit
        return super(StockMove, self)._get_price_unit()