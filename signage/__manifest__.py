# -*- coding: utf-8 -*-

{
    'name': 'Digital Signage',
    'version': '1.0',
    'summary': 'System for digital signage pages',
    'description': """
Digital Signage
===============
Financed by CEVT AB
* A signage is an information page
* A page can hold several areas
* Areas can be fetched separately or in a page
* An area can be of several types
* An area of type page consists of several subareas, each subarea are a template/view

    """,
    'author': 'Vertel AB',
    'website': 'http://www.vertel.se',
    'category': 'website',
    'sequence': 0,
    'depends': ['website'],
    'demo': [],
    'data': [
        'signage_view.xml',
        'templates.xml',
        'view/tmpl_demo_index.xml',
        'view/index.xml', # FIRST PAGE: Select, edit, post, publish and delete posts from the service.
        'view/tmpl_layout.xml',
        'view/tmpl_post_edit.xml',
        'view/tmpl_signage_overview.xml',
        'view/tmpl_signage_page_template.xml',
    ],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
