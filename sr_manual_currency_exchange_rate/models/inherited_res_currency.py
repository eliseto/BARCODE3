# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################

from odoo import models, fields, api

class ResCurrency(models.Model):
    _inherit = 'res.currency'

    @api.model
    def _get_conversion_rate(self, from_currency, to_currency, company, date):
#         print ("===========self._context",self._context)
        currency_rates = (from_currency + to_currency)._get_rates(company, date)
        if self._context.get('active_manutal_currency'):
            res = self._context.get('manual_rate')
        else:
            res = currency_rates.get(to_currency.id) / currency_rates.get(from_currency.id)
        print ("=====currency_rates===",currency_rates)
        print ("=======currency_rates.get(to_currency.id)",to_currency.name,currency_rates.get(to_currency.id))
        print ("=======currency_rates.get(from_currency.id)",from_currency.name,currency_rates.get(from_currency.id))
        print ("==========res",res)
        return res