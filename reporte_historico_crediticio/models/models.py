# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class reporte_historico_crediticio(models.Model):
#     _name = 'reporte_historico_crediticio.reporte_historico_crediticio'
#     _description = 'reporte_historico_crediticio.reporte_historico_crediticio'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
