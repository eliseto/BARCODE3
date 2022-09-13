# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResUsers(models.Model):

    _inherit = "res.users"

    comision_tabla_id = fields.Many2one('venta.comision.tabla', string='Comision')
