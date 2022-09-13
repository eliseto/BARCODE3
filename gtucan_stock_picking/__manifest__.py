# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2019 Xetechs, S.A. (<https://www.xetechs.com>).
#
#    For Module Support : laquino@xetechs.com --> Luis Aquino + 502 4814-3481
#
##############################################################################

{
    'name': 'Odoo Custom Stock Picking',
    'version': '1.0',
    'sequence': 1,
    'category': 'Generic Modules/Warehouse',
    'license': 'LGPL-3',
    'summary': 'Odoo Stock module customization',
    'description': """
        
    """,
    'depends': ['stock'],
    'data': [
        'data/stock_picking_order_sequence.xml',
        'views/stock_location_form.xml',
        'views/stock_picking_view.xml',
        'report/report_stockpicking_operations.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    
    'author': 'Guillermo Mejia --> gmejia@xetechs.com',
    'website': 'https://xetechs.odoo.com',    
    'maintainer': 'Xetechs, S.A.', 
    'support': 'gmejia@xetechs.com',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
