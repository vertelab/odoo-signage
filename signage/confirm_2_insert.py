#!/usr/bin/env python
# -*- coding: utf-8 -*- 
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

# THIS PROJECT IS COMPATIBLE WITH ODOO 10.
class WebsiteSignage(http.Controller):


    def force_to_unicode(text):
        # ~ "If text is unicode, it is returned as is. If it's str, convert it to Unicode using UTF-8 encoding"
        # ~ Source:
        # ~ https://gist.github.com/gornostal/1f123aaf838506038710
        return text if isinstance(text, unicode) else text.decode('utf8')


    # INSERT NEW MENU
    # MENU = SIGNAGE
    # FORM ACTION ="/signage/admin/menu/insert" >> POST
    @http.route(['/signage/admin/menu/insert'],type='http', auth='user', csrf=False, website=True)
    def signage_menu_insert(self, **post):

        title = ""
        if post.get('title') == "":
            title = "Showcase"
        else:
            title = post.get('title')
        
        # REPLACE FROM BAD/INVALID CHARS
        # ~ title = title.encode('utf-8')
        # ~ title = title.replace(" ", "_")
        # ~ title = title.replace("å", "a")
        # ~ title = title.replace("Å", "A")
        # ~ title = title.replace("ä", "a")
        # ~ title = title.replace("Ä", "A")
        # ~ title = title.replace("ö", "o")
        # ~ title = title.replace("Ö", "O")
       
        # LOOP AND CHECK FOR DUPLICATES! :-)
        while request.env['signage.signage'].search_count([('name', '=', title)]) > 0:
            arrTitle = title.split("_")
            if len(arrTitle) > 1:
                intCounter = int(arrTitle[1]) + 1
            else:
                intCounter = 1
            # NEW TITLE NAME
            title = arrTitle[0] + "_" + str(intCounter)
            
        template_id = request.env['ir.ui.view'].search([('key','=', post.get('default_layout') )] )
        #_logger.warn('<<<<<<<<<<<<<<<<<  template_id: %s' % template_id )

        if len(template_id) > 0:
            template_id = template_id[0].id
        else:
            template_id = None
    
        _logger.warn('<<<<<<<<<<<<<<<<<  template_id: %s' % template_id )
        _logger.warn('<<<<<<<<<<<<<<<<<  title: %s' % title )
        
        new_signage = request.env['signage.signage'].create({
            'name': title ,
            'name_url': title ,
            'template_id': template_id,
            'state': 'open',
            'description': 'Some important text!',
        })



        #new_signage.token = new_signage.get_token()
        new_signage.get_token()
        
        if new_signage.template_id:      
            for area in range(1, new_signage.template_id.number_of_areas +1):
                request.env['signage.area'].create({
                    'signage_id': new_signage.id,
                    'name': 'area_%s' % area ,
                })
        
        return werkzeug.utils.redirect('/signage/')

