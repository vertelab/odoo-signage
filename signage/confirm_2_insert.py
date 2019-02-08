# confirm_2_insert.py
# -*- coding: utf-8 -*-
##############################################################################
#
# Odoo, Open Source Enterprise Resource Management Solution, third party addon
# Copyright (C) 2019- Vertel AB (<http://vertel.se>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import api, fields, models,_
from odoo import http
from odoo.http import request
import hashlib
import datetime
# ~ import math
import werkzeug
from werkzeug.exceptions import NotFound

import logging
_logger = logging.getLogger(__name__)

# GENERIC CODE FOR ROUTING
# 1. ROUTING (INDEX / SHOW)
# 2. INSERT <--- ***
# 3. UPDATE
# 4. DELETE
# 5. UNASSIGNED / OTHER
# CODE + PROJECT IS COMPATIBLE WITH ODOO 10.
class WebsiteSignage(http.Controller):

    # INSERT NEW MENU
    # MENU = SIGNAGE
    # FORM ACTION ="/signage/admin/menu/insert" >> POST
    @http.route(['/signage/admin/menu/insert'],type='http', auth='user', csrf=False, website=True)
    def signage_menu_insert(self, **post):
        intAreas = 0
        
        if post.get('default_layout') == "showcase_1":
            intAreas = 1
            intTemplateID = 1
        elif post.get('default_layout') == "showcase_2_1":
            intAreas = 2
            intTemplateID = 2
        elif post.get('default_layout') == "showcase_2_2":
            intAreas = 2
            intTemplateID = 3
        elif post.get('default_layout') == "showcase_3_1":
            intAreas = 3
            intTemplateID = 4
        elif post.get('default_layout') == "showcase_3_2":
            intAreas = 3
            intTemplateID = 5
        elif post.get('default_layout') == "showcase_3_3":
            intAreas = 3
            intTemplateID = 6
        elif post.get('default_layout') == "showcase_4":
            intAreas = 4
            intTemplateID = 7
        elif post.get('default_layout') == "showcase_5_1":
            intAreas = 5
            intTemplateID = 8
        elif post.get('default_layout') == "showcase_5_2":
            intAreas = 5
            intTemplateID = 9
             
        # ~ _logger.warn('<<<<<<<<<<<<<<<<<  intAreas: %s' % intAreas )
        # ~ _logger.warn('<<<<<<<<<<<<<<<<<  title: %s' % post.get('title'))
        # ~ _logger.warn('<<<<<<<<<<<<<<<<<  default_layout: %s' % post.get('default_layout') )
        # ~ _logger.warn('<<<<<<<<<<<<<<<<<  default_layout: %s' % post.get('default_layout')[0] )
        # ~ _logger.warn('<<<<<<<<<<<<<<<<<  default_layout: %s' % request.env['ir.ui.view'].search([('key','=', post.get('default_layout'))]) )
        # ~ _logger.warn('<<<<<<<<<<<<<<<<<  default_layout: %s' % request.env['ir.ui.view'].search([('key','=', post.get('default_layout')[0])]) )
        title = ""
        if post.get('title') == "":
            title = "Showcase"
        else:
            title = post.get('title')

        new_signage = request.env['signage.signage'].create({
            'name': title ,
            'template_id': request.env['ir.ui.view'].search([('key','=', post.get('default_layout')[0])])
        })
        
        # LOOP THOUGH ALL AREAS, AS SELECTED
        i = 1
        # ~ while i < intAreas:
                       
            # ~ intAreas += 1
        
        return werkzeug.utils.redirect('/signage/')

