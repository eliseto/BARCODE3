# -*- coding: utf-8 -*-

from datetime import date, datetime
from odoo import models,api
import string

class VentaComisionExcel(models.AbstractModel):
    _name = 'report.venta_comision.venta_comision_excel'
    _description = 'Reporte de Comisiones XLS'
    _inherit = 'report.report_xlsx.abstract'


    def generate_xlsx_report(self, workbook, data, data_report):
        bold = workbook.add_format({'bold': True})
        bold_numerico = workbook.add_format({'bold': True, 'num_format': '#,##0.00'})
        fnumerico = workbook.add_format({'num_format': '#,##0.00'})
        data_format1 = workbook.add_format({'bg_color': '#A1B3DB', 'bold': True})
        data_format2 = workbook.add_format({'bg_color': '#FF5E33', 'bold': True, 'num_format': '#,##0.00'})
        data_format3 = workbook.add_format({'bg_color': '#FFBE33', 'bold': True, 'num_format': '#,##0.00'})
        data_format4 = workbook.add_format({'bg_color': '#FF0000',})
        porcentaje = workbook.add_format({'num_format': '0.00%'})
        formato_fecha = workbook.add_format({'num_format': 'dd/mm/yyyy'})
        sheet_libro = workbook.add_worksheet('Analisis')

        venta_comision_id = data['venta_comision_id']

        fila=0;
        sheet_libro.write(fila, 0, "Fecha Factura", bold)
        sheet_libro.write(fila, 1, "Cliente", bold)
        sheet_libro.write(fila, 2, "Numero", bold)
        #sheet_libro.write(fila, 3, "Cliente", bold)
        sheet_libro.write(fila, 3, "Venta", bold)
        #sheet_libro.write(fila, 4, "Costo", bold)
        #sheet_libro.write(fila, 5, "Utilidad", bold)
        #sheet_libro.write(fila, 6, "% de Utilidad", bold)
        #sheet_libro.write(fila, 7, "Pago ID", bold)
        #sheet_libro.write(fila, 8, "Pago", bold)
        sheet_libro.write(fila, 4, "Fecha Pago", bold)
        sheet_libro.write(fila, 5, "Pago Monto", bold)

        #sheet_libro.write(fila, 6, "EXEN", bold)
        #sheet_libro.write(fila, 7, "RETEN IVA", bold)

        sheet_libro.write(fila, 6, "Abono", bold)
        sheet_libro.write(fila, 7, "Anticipo", bold)
        sheet_libro.write(fila, 8, "Nota de Credito", bold)
        sheet_libro.write(fila, 9, "Nota de Abono", bold)
        sheet_libro.write(fila, 10, "IVA", bold)
        sheet_libro.write(fila, 11, "Pago Total", bold)
        sheet_libro.write(fila, 12, "Comision", bold)
        sheet_libro.set_column(0, 0, 10)
        sheet_libro.set_column(1, 1, 40)
        sheet_libro.set_column(2, 2, 15)
        sheet_libro.set_column(3, 3, 25)
        sheet_libro.set_column(4, 4, 15)
        sheet_libro.set_column(5, 5, 15)
        sheet_libro.set_column(6, 6, 15)
        sheet_libro.set_column(9, 9, 20)
        sheet_libro.set_column(10, 10, 13)
        sheet_libro.set_column(11, 20, 15)




        venta_comision_lines = self.env['venta.comision.line'].read_group([('comision_id', '=', venta_comision_id),], ['vendedor_id','almacen_id'], ['vendedor_id','almacen_id'], lazy=False)


        #lista_vendedores = self.get_Listado_Vendedor_tienda(venta_comision_id)
        total = {}
        total['precio_sin_iva'] = 0
        total['costo'] = 0
        total['utilidad'] = 0
        total['pago_monto'] = 0
        total['pago_abono'] = 0
        total['pago_anticipo'] = 0
        total['nota_abono_monto'] = 0
        total['iva'] = 0
        total['pago_total_sin_iva'] = 0
        total['nota_credito_monto'] = 0
        total['exenciones_iva'] = 0
        total['retenciones_iva'] = 0
        total['nota_abono_monto'] = 0
        total['comision'] = 0

        for vendedor in venta_comision_lines:
            fila += 1
            sheet_libro.set_row(fila, cell_format=data_format1)
            vendedor_user = self.env["res.users"].browse(vendedor['vendedor_id'][0])
            sheet_libro.write(fila, 0, vendedor_user.name)

            add_domain = []
            if vendedor['almacen_id']:
                almacen = self.env["stock.warehouse"].browse(vendedor['almacen_id'][0])
                add_domain = [('almacen_id', '=', almacen.id)]
                sheet_libro.write(fila, 4, almacen.name)
            else:
                add_domain = [('almacen_id', '=', False)]


            venta_comision_lines_clientes = self.env['venta.comision.line'].read_group([
                        ('comision_id', '=', venta_comision_id)
                        ,('vendedor_id','=',vendedor_user.id)
                        ]+add_domain,
                        ['vendedor_id','almacen_id','cliente_id'],
                        ['vendedor_id','almacen_id','cliente_id'], lazy=False)
            vendedor_sub_total = {}
            vendedor_sub_total['precio_sin_iva'] = 0
            vendedor_sub_total['costo'] = 0
            vendedor_sub_total['utilidad'] = 0
            vendedor_sub_total['pago_monto'] = 0
            vendedor_sub_total['pago_abono'] = 0
            vendedor_sub_total['pago_anticipo'] = 0
            vendedor_sub_total['nota_credito_monto'] = 0
            vendedor_sub_total['nota_abono_monto'] = 0
            vendedor_sub_total['exenciones_iva'] = 0
            vendedor_sub_total['retenciones_iva'] = 0
            vendedor_sub_total['comision'] = 0
            vendedor_sub_total['iva'] = 0
            vendedor_sub_total['pago_total_sin_iva'] = 0
            for cliente in venta_comision_lines_clientes:
                fila += 1

                factura_cliente = self.env["res.partner"].browse(cliente['cliente_id'][0])
                sheet_libro.write(fila, 0, factura_cliente.ref, bold)
                sheet_libro.write(fila, 1, factura_cliente.name, bold)

                clientes_facturas = self.env['venta.comision.line'].search([
                        ('comision_id', '=', venta_comision_id)
                        ,('vendedor_id','=',vendedor_user.id)
                        ,('cliente_id','=',factura_cliente.id)
                        ]+add_domain)
                cliente_sub_total = {}
                cliente_sub_total['precio_sin_iva'] = 0
                cliente_sub_total['costo'] = 0
                cliente_sub_total['utilidad'] = 0
                cliente_sub_total['pago_monto'] = 0
                cliente_sub_total['pago_abono'] = 0
                cliente_sub_total['pago_anticipo'] = 0
                cliente_sub_total['nota_credito_monto'] = 0
                cliente_sub_total['nota_abono_monto'] = 0
                cliente_sub_total['exenciones_iva'] = 0
                cliente_sub_total['retenciones_iva'] = 0
                cliente_sub_total['comision'] = 0
                cliente_sub_total['iva'] = 0
                cliente_sub_total['pago_total_sin_iva'] = 0
                for factura in clientes_facturas:
                    fila += 1

                    sheet_libro.write(fila, 0, factura.factura_id.invoice_date, formato_fecha)
                    #sheet_libro.write(fila, 1, str(factura.factura_id.id) +") " +factura.factura_id.journal_id.name)
                    sheet_libro.write(fila, 1, factura_cliente.name)
                    sheet_libro.write(fila, 2, factura.factura_id.name)
                    #sheet_libro.write(fila, 22, factura.factura_id.invoice_payment_state)
                    sheet_libro.write(fila, 3, factura['precio_sin_iva'], fnumerico)
                    #sheet_libro.write(fila, 5, factura['costo'], fnumerico)
                    #sheet_libro.write(fila, 6, factura['utilidad'], fnumerico)
                    #sheet_libro.write(fila, 7, factura['porcentaje_utilidad'], porcentaje)
                    if 'pago_id' in factura:
                        if factura.pago_id:
                            #sheet_libro.write(fila, 8, factura.pago_id.id)
                            #sheet_libro.write(fila, 9, factura['pago_name'])
                            sheet_libro.write(fila, 4, factura['pago_date'], formato_fecha)
                    sheet_libro.write(fila, 5, factura['pago_monto'], fnumerico)

                    #sheet_libro.write(fila, 6, factura['exenciones_iva'], fnumerico)
                    #sheet_libro.write(fila, 13, factura['retenciones_iva'], fnumerico)

                    sheet_libro.write(fila, 6, factura['pago_abono'], fnumerico)
                    sheet_libro.write(fila, 7, factura['pago_anticipo'], fnumerico)
                    if 'nota_credito_monto' in factura:
                        sheet_libro.write(fila, 8, factura['nota_credito_monto'], fnumerico)
                    if 'nota_abono_monto' in factura:
                        sheet_libro.write(fila, 9, factura['nota_abono_monto'], fnumerico)
                    if 'nota_sin_clasificar' in factura:
                        sheet_libro.write(fila, 9, factura['nota_sin_clasificar'])
                    sheet_libro.write(fila, 10, factura['iva'], fnumerico)
                    sheet_libro.write(fila, 11, factura['pago_total_sin_iva'], fnumerico)
                    sheet_libro.write(fila, 12, factura['comision'], fnumerico)
                    if not factura['corresponde']:
                        sheet_libro.set_row(fila, cell_format=data_format4)

                    cliente_sub_total['precio_sin_iva'] += factura['precio_sin_iva']
                    cliente_sub_total['costo'] += factura['costo']
                    cliente_sub_total['utilidad'] += factura['utilidad']
                    cliente_sub_total['pago_monto'] += factura['pago_monto']
                    cliente_sub_total['pago_abono'] += factura['pago_abono']
                    cliente_sub_total['pago_anticipo'] += factura['pago_anticipo']
                    cliente_sub_total['nota_credito_monto'] += factura['nota_credito_monto']
                    cliente_sub_total['nota_abono_monto'] += factura['nota_abono_monto']
                    cliente_sub_total['exenciones_iva'] += factura['exenciones_iva']
                    cliente_sub_total['retenciones_iva'] += factura['retenciones_iva']
                    cliente_sub_total['iva'] += factura['iva']
                    cliente_sub_total['pago_total_sin_iva'] += factura['pago_total_sin_iva']
                    cliente_sub_total['comision'] += factura['comision']

                fila += 1
                sheet_libro.write(fila, 1, 'CLIENTE')
                sheet_libro.write(fila, 3, cliente_sub_total['precio_sin_iva'], bold_numerico)
                #sheet_libro.write(fila, 5, cliente_sub_total['costo'], bold_numerico)
                #sheet_libro.write(fila, 6, cliente_sub_total['utilidad'], bold_numerico)
                sheet_libro.write(fila, 5, cliente_sub_total['pago_monto'], bold_numerico)
                #sheet_libro.write(fila, 12, cliente_sub_total['exenciones_iva'], bold_numerico)
                #sheet_libro.write(fila, 13, cliente_sub_total['retenciones_iva'], bold_numerico)
                sheet_libro.write(fila, 6, cliente_sub_total['pago_abono'], bold_numerico)
                sheet_libro.write(fila, 7, cliente_sub_total['pago_anticipo'], bold_numerico)
                sheet_libro.write(fila, 8, cliente_sub_total['nota_credito_monto'], bold_numerico)
                sheet_libro.write(fila, 9, cliente_sub_total['nota_abono_monto'], bold_numerico)
                sheet_libro.write(fila, 10, cliente_sub_total['iva'], bold_numerico)
                sheet_libro.write(fila, 11, cliente_sub_total['pago_total_sin_iva'], bold_numerico)
                sheet_libro.write(fila, 12, cliente_sub_total['comision'], bold_numerico)
                sheet_libro.set_row(fila, cell_format=bold)

                vendedor_sub_total['precio_sin_iva'] += cliente_sub_total['precio_sin_iva']
                vendedor_sub_total['costo'] += cliente_sub_total['costo']
                vendedor_sub_total['utilidad'] += cliente_sub_total['utilidad']
                vendedor_sub_total['pago_monto'] += cliente_sub_total['pago_monto']
                vendedor_sub_total['pago_abono'] += cliente_sub_total['pago_abono']
                vendedor_sub_total['pago_anticipo'] += cliente_sub_total['pago_anticipo']
                vendedor_sub_total['nota_credito_monto'] += cliente_sub_total['nota_credito_monto']
                vendedor_sub_total['nota_abono_monto'] += cliente_sub_total['nota_abono_monto']
                vendedor_sub_total['exenciones_iva'] += cliente_sub_total['exenciones_iva']
                vendedor_sub_total['retenciones_iva'] += cliente_sub_total['retenciones_iva']
                vendedor_sub_total['iva'] += cliente_sub_total['iva']
                vendedor_sub_total['pago_total_sin_iva'] += cliente_sub_total['pago_total_sin_iva']
                vendedor_sub_total['comision'] += cliente_sub_total['comision']

            fila += 1
            sheet_libro.write(fila, 1, 'VENDEDOR')
            sheet_libro.write(fila, 3, vendedor_sub_total['precio_sin_iva'])
            #sheet_libro.write(fila, 5, vendedor_sub_total['costo'])
            #sheet_libro.write(fila, 6, vendedor_sub_total['utilidad'])
            sheet_libro.write(fila, 5, vendedor_sub_total['pago_monto'])

            #sheet_libro.write(fila, 12, vendedor_sub_total['exenciones_iva'])
            #sheet_libro.write(fila, 13, vendedor_sub_total['retenciones_iva'])


            sheet_libro.write(fila, 6, vendedor_sub_total['pago_abono'])
            sheet_libro.write(fila, 7, vendedor_sub_total['pago_anticipo'])
            sheet_libro.write(fila, 8, vendedor_sub_total['nota_credito_monto'])
            sheet_libro.write(fila, 9, vendedor_sub_total['nota_abono_monto'])
            sheet_libro.write(fila, 10, vendedor_sub_total['iva'])
            sheet_libro.write(fila, 11, vendedor_sub_total['pago_total_sin_iva'])
            sheet_libro.write(fila, 12, vendedor_sub_total['comision'])
            sheet_libro.set_row(fila, cell_format=data_format2)

            total['precio_sin_iva'] += vendedor_sub_total['precio_sin_iva']
            total['costo'] += vendedor_sub_total['costo']
            total['utilidad'] += vendedor_sub_total['utilidad']
            total['pago_monto'] += vendedor_sub_total['pago_monto']
            total['pago_abono'] += vendedor_sub_total['pago_abono']
            total['pago_anticipo'] += vendedor_sub_total['pago_anticipo']
            total['nota_credito_monto'] += vendedor_sub_total['nota_credito_monto']
            total['nota_abono_monto'] += vendedor_sub_total['nota_abono_monto']
            total['retenciones_iva'] += vendedor_sub_total['retenciones_iva']
            total['exenciones_iva'] += vendedor_sub_total['exenciones_iva']
            total['iva'] += vendedor_sub_total['iva']
            total['pago_total_sin_iva'] += vendedor_sub_total['pago_total_sin_iva']
            total['comision'] += vendedor_sub_total['comision']


        fila += 1
        sheet_libro.write(fila, 1, 'TOTAL')
        sheet_libro.write(fila, 3, total['precio_sin_iva'])
        #sheet_libro.write(fila, 5, total['costo'])
        #sheet_libro.write(fila, 6, total['utilidad'])
        sheet_libro.write(fila, 5, total['pago_monto'])

        #sheet_libro.write(fila, 12, total['retenciones_iva'])
        #sheet_libro.write(fila, 13, total['exenciones_iva'])

        sheet_libro.write(fila, 6, total['pago_abono'])
        sheet_libro.write(fila, 7, total['pago_anticipo'])
        sheet_libro.write(fila, 8, total['nota_credito_monto'])
        sheet_libro.write(fila, 9, total['nota_abono_monto'])
        sheet_libro.write(fila, 10, total['iva'])
        sheet_libro.write(fila, 11, total['pago_total_sin_iva'])
        sheet_libro.write(fila, 12, total['comision'])
        sheet_libro.set_row(fila, cell_format=data_format3)
