# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Puslitbang Polri Survey',
    'version': '2.0',
    'category': 'Marketing',
    'description': """
Customize your surveys, gather answers and print statistics
    """,
    'summary': 'Create surveys, collect answers and print statistics',
    'website': 'https://www.odoo.com/page/survey',
    'depends': ['mail', 'website', 'survey'],
    'data': [
        'wizard/survey_generator.xml',
        'views/survey_views.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}