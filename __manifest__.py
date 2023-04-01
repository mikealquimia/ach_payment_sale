# -*- coding: utf-8 -*-
{
    'name': "Payment Sale",

    'summary': """ """,
    'description': """ """,
    'author': "ACH",
    'website': "http://www.yourcompany.com",
    'license': 'LGPL-3',
    'category': 'Sales',
    'version': '0.1',
    'depends': ['base',
                'account',
                'sale',
                'sale_management '
    ],
    'data': [
        #'security/ir.model.access.csv',
        'security/payment_sale.xml',
        'views/sale_order_views.xml',
        'views/account_payment_views.xml',
        'views/account_invoice_views.xml',
    ],
}