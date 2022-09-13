# -*- coding: utf-8 -*-
# Part of servisoft latam. See LICENSE file for full copyright and licensing details.
{
    "name" : "Tasa de cambio de moneda manual en factura/pago/venta/compra en Odoo",
    "version" : "15.0.0.0",
    "depends" : ['base','account','purchase','sale_management','stock'],
    "author": "Servisoft Latam",
    "summary": " con este modulo tendrá la opción de establecer las tasas de cambio de divisas de forma manual/directa en las facturas de los clientes, las facturas de los proveedores, las órdenes de venta, las órdenes de compra y el pago de la cuenta en cada registro y cubrir todo el flujo de trabajo de Odoo",
    "description": """
   

    """,
    'category': 'Accounting',
    "autor" : "JIMMY ARAUJO",
    "data" :[
             "views/customer_invoice.xml",
             "views/account_payment_view.xml",
             "views/purchase_view.xml",
             "views/sale_view.xml",
        ],
    'qweb':[],
    "auto_install": False,
    "installable": True,
    "images":['static/description/Banner.png'],
    "license": "OPL-1",
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
