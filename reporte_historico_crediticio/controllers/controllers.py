# -*- coding: utf-8 -*-
# from odoo import http


# class ReporteHistoricoCrediticio(http.Controller):
#     @http.route('/reporte_historico_crediticio/reporte_historico_crediticio', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/reporte_historico_crediticio/reporte_historico_crediticio/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('reporte_historico_crediticio.listing', {
#             'root': '/reporte_historico_crediticio/reporte_historico_crediticio',
#             'objects': http.request.env['reporte_historico_crediticio.reporte_historico_crediticio'].search([]),
#         })

#     @http.route('/reporte_historico_crediticio/reporte_historico_crediticio/objects/<model("reporte_historico_crediticio.reporte_historico_crediticio"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('reporte_historico_crediticio.object', {
#             'object': obj
#         })
