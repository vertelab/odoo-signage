# confirm_1_routing.py
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
# 1. ROUTING (INDEX / SHOW) <--- ***
# 2. INSERT
# 3. UPDATE
# 4. DELETE
# 5. UNASSIGNED / OTHER
# THIS PROJECT IS COMPATIBLE WITH ODOO 10.
class WebsiteSignage(http.Controller):
    # ORDER BY...:
    # https://www.odoo.com/forum/help-1/question/how-to-order-by-odoo-10-145924
    # <ul t-foreach="signages.sorted(lambda s: s.template_id)" t-as="signage">
    @http.route(['/signage','/signage/list'],type='http', auth='user', website=True)
    def signage_list(self, **post):
        return request.render('signage.signage_list', {'signages': request.env['signage.signage'].search([('state','=','open')], order='name asc')})
        # ~ return request.render('signage.signage_list', {'signages': request.env['signage.signage'].search([('state','=','open')])})
        # ~ return request.render('signage.signage_list', {'signages': request.env['signage.signage'].search([('state','=','open')]).order='name, date'})

# ~ .search([('xyz')],limit=10,offset=offset(0,10,20,30),order='name,date')

    @http.route(['/signage/overview'],type='http', auth='user', website=True)
    def signage_overview(self, **post):
        return request.render('signage.signage_overview', {'signages': request.env['signage.signage'].search([('state','=','open')])})

    # NEW PROJECT
    # /[project]/admin/menu/insert
    @http.route(['/signage/menu/insert'],type='http', auth='user', website=True)
    def signage_new_project(self, **post):
        # ~ return request.render('signage.signage_overview', {'signages': request.env['signage.signage'].search([('state','=','open')])})
        # ~ return request.render('signage.signage_overview', {'signages': request.env['signage.signage'].search([('state','=','open')])})
        return werkzeug.utils.redirect('/signage/' )


    # DIRECT URL TO THE ROTATING PAGE
    # SHOW + TOKEN
    # /signage/view/menu/{menu.name}/all?token=123
    @http.route(['/signage/view/menu/<string:signage>/all'],type='http', auth='public', website=True)
    def signage_view_all(self, signage, **post): #return the last page from a specified area
        signage = request.env['signage.signage'].sudo().search([('name_url', '=', signage)])
        if signage:
            if signage.token and post.get('token') and signage.token == post.get('token'):
                area_list = []
                for area in signage.area_ids.sorted(lambda a: a.name):
                    res = area.get_next_page().template_id.render({'signage': signage, 'area': area, 'page': area.last_page, 'hide_header': True})
                    area_list.append(res)
                return request.render(signage.template_id.key, {'signage': signage, 'area_list': area_list})
            else:
                return request.render('website.403', {})
        return False

