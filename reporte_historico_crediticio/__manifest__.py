# -*- coding: utf-8 -*-
{
    'name': "Reporte Historico Crediticio",

    'summary': """
        Reporte Historico Crediticio""",

    'description': """
        Reporte Historico Crediticio
    """,

    'author': "Gerson Ovalle",
    'website': "http://www.xetechs.com",
    'license': 'LGPL-3',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'report/reporte_historico.xml',
        'views/views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
