# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class ProductDai(models.Model):
    _name = 'product.dai'
    _description = 'Arancel'

    name = fields.Char(string='Codigo', required=True)
    descripcion = fields.Char(string='Descripcion')
    porcentaje = fields.Integer(string='Porcentaje', required=True)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    dai_id = fields.Many2one('product.dai', string='DAI', help='Select a DAI for this product')
    sat_tipo_producto = fields.Selection([
		('bien','Bien'),
		('servicio','Servicio'),
		('exento','Excento'),
		('gas','Combustible'),
		('exp_in_ca_bien', 'Exportacion Bien in CA'),
		('imp_in_ca_bien', 'Importacion Bien in CA'),
		('imp_out_ca_bien', 'Importacion Bien out CA'),
		])
