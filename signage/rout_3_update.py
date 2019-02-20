# confirm_3_update.py
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
# 2. INSERT
# 3. UPDATE <--- ***
# 4. DELETE
# 5. UNASSIGNED / OTHER
# THIS PROJECT IS COMPATIBLE WITH ODOO 10.
class WebsiteSignage(http.Controller):

    # UPDATE POST
    # /signage/admin/post/{post.id}/edit
    @http.route(['/signage/admin/post/<model("signage.area.page"):page>/edit'],type='http', auth='user', website=True)
    def signage_edit_page(self, page, **post): # return a specified page and activate edit mode
        return request.render(page.template_id.key, {'signage': page.area_id.signage_id, 'area': page.area_id, 'page': page, 'edit': True, 'hide_header' : False})

    # UPDATE NAME FOR POST
    # /[project]/admin/post/{menuId.id}/{post.id}/edit
    @http.route(['/signage/admin/post/<model("signage.signage"):signage>/<model("signage.area.page"):page>/edit'],type='http', auth='user', website=True)
    def update_postId (self, signage, page):
        #_logger.warn('<<<<<<<<<<<<<<<<<  signage = %s' % signage)
        #_logger.warn('<<<<<<<<<<<<<<<<<  postId = %s' % page)
        page.write(name, 'name')
        return werkzeug.utils.redirect('/signage/admin/menu/%s/edit' % signage.id)
    
    
    # UPDATE NAME FOR POST
    # /[project]/admin/post/{menuId.id}/{post.id}/edit
    @http.route(['/signage/admin/post/<model("signage.signage"):signage>/<model("signage.area.page"):page>/edit'],type='http', auth='user', website=True)
    def update_postId (self, signage, page):
        #_logger.warn('<<<<<<<<<<<<<<<<<  signage = %s' % signage)
        #_logger.warn('<<<<<<<<<<<<<<<<<  postId = %s' % page)
        page.write(name, 'name')
        return werkzeug.utils.redirect('/signage/admin/menu/%s/edit' % signage.id)
        
