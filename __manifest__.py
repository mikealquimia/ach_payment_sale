# -*- coding: utf-8 -*-
{
    'name': "Payment Sale",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    'description': """
        Long description of module's purpose
    """,
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base',
                'account',
                'sale',

    ],
    'data': [
        # 'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'views/account_payment_views.xml',
        'views/account_invoice_views.xml',
    ],
}