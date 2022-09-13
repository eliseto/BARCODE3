# -*- coding: utf-8 -*-
# from odoo import http


# class VentaComision(http.Controller):
#     @http.route('/venta_comision/venta_comision/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/venta_comision/venta_comision/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('venta_comision.listing', {
#             'root': '/venta_comision/venta_comision',
#             'objects': http.request.env['venta_comision.venta_comision'].search([]),
#         })

#     @http.route('/venta_comision/venta_comision/objects/<model("venta_comision.venta_comision"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('venta_comision.object', {
#             'object': obj
#         })
