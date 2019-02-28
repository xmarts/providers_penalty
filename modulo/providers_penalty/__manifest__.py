# -*- coding: utf-8 -*-
{
    'name': "Providers_penalty",

    'summary': """
        Penalty to supplier for late delivery""",

    'description': """
        This module has the functionality of comparing the current date with
        the purchase order date, if the current date is greater than the date 
        of the order the system will not allow validating the order until the 
        user ticks the box where it will indicate that it is according to the 
        delivery, once you check the box you can validate the order automatically 
        an invoice will be created if there is none and a credit note related to 
        the order where a penalty of five percent of the total amount will be applied.
    """,

    'author': "Xmarts",
    'contributors': "Gilberto Santiago Acevedo",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}