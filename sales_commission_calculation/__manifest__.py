# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Sales Commission by Sales/Invoice/Payment',
    'version' : '1.8.1',
    'price' : 99.0,
    'currency': 'EUR',
    'category': 'Sales',
    'license': 'Other proprietary',
    'live_test_url': 'https://youtu.be/ODTn5kepVww', #'https://youtu.be/-wK3ouvQw2I',
    'images': ['static/description/img1.jpg'],
    'description': """
Sales Commission by Sales/Invoice/Payment
Odoo 10 Sales Commission/Incentive Calculations
Incentive Calculations
Sales Commission
sale_commission_gt
Odoo 10 Sales Commission/Incentive Calculations Based on Sales, Payments Received & Invoicing
Easily Manage Complex Commission or Incentive Plans to Enhance Corporate Goals

Odoo Sales Commission / Incentive Management module offers you with following features:

Calculate Sales commission based on :
Sale Validation
Invoice Validation
Payment Validation
Products Sold
product Category
Sales Team
Automate payments via approval for incentives.
Linked with Accounting
Manage Journals separately
Manage payable commission
Pay Commission
Paid Commission
After installation Odoo Sales Commission Module

1. Sales Validation & Product
2. Sales Validation & Product Category
3. Sales Validation & Sales Team
4. Invoice validation & Product
5. Invoice validation & Product Category
6. Invoice validation & Sales Team
7. Payment validation & Product
8. Payment validation & Product Category
9. Payment validation & Sales Team

sales Commission
sale_commission
sales_Commission
sale Commission
sales Commissions
sales order Commission
order Commission
sales person Commission
sales team Commission
sale team Commission
sale person Commission
team Commission
Commission
sales order on Commission
invoice on Commission
payment on Commission
Commission invoice
Commission vendor invoice
sales Commision
Commission sales user invoice

Sales Commission (form)
Sales Commission (form)
Sales Commission List (tree)
Sales Commission List (tree)
Sales Commission Search (search)
Sales Commission Search (search)
sales_commission_id (qweb)
sales_commission_worksheet_id (qweb)

Sales Commission by Sales/Invoice/Payment

This module provide feature to manage sales commision by Sales/Invoice/Payments


This module allow company to manage sales commision with different options. You can configure after installing module what option/policy your company is following to give commissions to your sales users.
We are allowing you to select When to Pay and Calculation based on . Here you can define policy which will be used to give commission to your sales team.


For every Calcalulation based on we are allowing you to select:
1. Sales Manager Commission %
2. Sales Person Commission %

If you keep Sales Manager Commission 0% then system will not create sales commision lines and sales commision worksheet. System will work only with single option at time ie for example you can select When to Pay = Invoice confirm and calculation based on = Product category so system will run on that and create commission.

Please note that When to Pay = Customer payment is only supported with Calculation based on Sales Team. - Other options are supported in matrix. 
Workflow will be:
Option1 : Sales Confirmation -> Create Sales commission worksheet (if not created for current month) -> Add Sales commission lines on worksheet -> For every sales of current month, system will append sales commission lines on worksheet. -> End of month Accouant may review worksheet and create commision invoice to pay/release commision to sales person.
Option2 : Invoice Validate -> Create Sales commission worksheet (if not created for current month) -> Add Sales commission lines on worksheet -> For every invoice validation of current month, system will append sales commission lines on worksheet. -> End of month Accouant may review worksheet and create commision invoice to pay/release commision to sales person.
Option3 : Customer Payment -> Create Sales commission worksheet (if not created for current month) -> Add Sales commission lines on worksheet -> For every payment from customer of current month, system will append sales commission lines on worksheet. -> End of month Accouant may review worksheet and create commision invoice to pay/release commision to sales person.
Commission to sales person always will be in company currency. Multi currency is supported for this module so sales order/ invoice / payment can be in different currency but system will take care for it and create commission lines in company currency.
Sales Commission product is created using data and you still can change commission product on commission worksheet to create commission invoice.

Menus
---- Invoicing/Commissions
---- ---- Invoicing/Commissions/Commission Worksheets
---- ---- Invoicing/Commissions/Sales Commissions Lines
---- Sales/Commissions
---- ---- Sales/Commissions/Commission Worksheets
---- ---- Sales/Commissions/Sales Commissions Lines

Configuration for Sales Commission

Commission to sales person always will be in company currency. Multi currency is supported for this module so sales order/ invoice / payment can be in different currency but system will take care for it and create commission lines in company currency.
Sales Commission product is created using data and you still can change commission product on commission worksheet to create commission invoice.
Commission amount will be based on Net Revenue Model where it consider amounts without taxes. (This module does not support Gross Margin Model)



            """,
    'summary' : 'This module provide feature to manage sales commision by Sales/Invoice/Payments',
    'author' : 'Probuse Consulting Service Pvt. Ltd.',
    'website' : 'wwww.probuse.com',
    'depends' : ['account','sale_management'],
    'support': 'contact@probuse.com',
    'data' : [
            'security/ir.model.access.csv',
            'security/sales_commission_security.xml',
            'data/commission_sequence.xml',
            'data/product_data.xml',
            'view/sale_config_settings_views.xml',
              'view/crm_team_view.xml',
              'view/product_template_view.xml',
#               'view/product_view.xml',
              'view/product_category_view.xml',
            'view/sales_commission_view.xml',
            'view/account_invoice_view.xml',
            'view/report_sales_commission.xml',
            'view/report_sales_commission_worksheet.xml',
            'view/account_payment.xml',
            'view/sale_view.xml',
              ],
    'installable' : True,
    'images': ['static/description/im2.jpg'],
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
