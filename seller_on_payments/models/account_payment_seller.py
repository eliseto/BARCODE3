# -*- coding: utf-8 -*-
##############################################################################
#
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT


class AccountPaymentSeller(models.Model):
    _inherit = "account.payment"

    vendedor_id = fields.Many2one('res.users', string='Vendedor', copy=False) 


class AccountPaymentSellerRegister(models.TransientModel):
    _inherit = "account.payment.register"

    vendedor_id = fields.Many2one('res.users', string='Vendedor') 

    def _create_payment_vals_from_wizard(self):
        res = super(AccountPaymentSellerRegister, self)._create_payment_vals_from_wizard()
        for rec in self:
            res.update({
                'vendedor_id': rec.vendedor_id.id or False,
            })
        return res
