# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2019 - Today Xetechs, S.A. (<https://www.xetechs.com>).
#
#    For Module Support : Luis Aquino --> laquino@xetechs.com 
#
##############################################################################
from collections import defaultdict
from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp
from odoo.addons.stock_landed_costs.models import product
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    arancel_id = fields.Many2one('arancel.type', 'Arancel', required=False, help="Seleccionar el arancel que aplica para este producto.")


class ArancelType(models.Model):
    _name = "arancel.type"
    _description = "Tipo de Arancel"

    name = fields.Char('Arancel', required=True)
    amount_arancel = fields.Float('Tasa arancel', required=True, help="Tasa porcentual de arancel")

