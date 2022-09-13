# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Xetechs, S.A. (https://xetechs.odoo.com)
#
#    For Module Support : laquino@xetechs.com --> + (502) 4814-3481
#
##############################################################################
{
    'name': 'Odoo Landed cost on Average Costing',
    'version': '1.0',
    'sequence': 1,
    'category': 'Generic Modules/Warehouse',
    'summary': 'odoo Apps will calculate average costing on landed Cost',
    'description': """
        odoo module will calculate average cost on landed costing
        
        
        odoo landed cost 
        odoo Average costing on landed cost 
        odoo landed cost with Average costing  
 Odoo Landed cost on Average Costing
Landed cost on Average costing 
odoo app will helps you to calculate Landed cost when product costing method is average
app will helps you to calculate Landed cost when product costing method is average
Calculate Landed cost when product costing method is average
Odoo Calculate Landed cost when product costing method is average
Create landed cost and validate 
Odoo create landed cost and validate 
Product cost price after validate landed cost 
Odoo product cost price after validate landed cost 
Product average costing 
Odoo product average costing 
Manage product average costing 
Odoo manage product average costing 
Average costing 
Odoo average costing 
Manage average costing 
Odoo manage average costing 
Manage product cost price 
Odoo manage product cost price 
Product landed cost 
Odoo product landed cost 
Manage product landed cost 
Odoo manage product landed cost 
       
        
        
    """,
    'depends': ['stock_landed_costs'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template_view.xml',
    ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    
    'author': 'Luis Aquino --> laquino@xetechs.com',
    'license': 'LGPL-3',
    'website': 'https://xetechs.odoo.com',    
    'maintainer': 'Xetechs, S.A.', 
    'support': 'laquino@xetechs.com',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
