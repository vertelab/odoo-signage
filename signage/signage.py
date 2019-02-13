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

from bokeh.io import show, output_file
from bokeh.models import ColumnDataSource
from bokeh.palettes import Spectral6
from bokeh.plotting import figure
from bokeh.transform import factor_cmap
from bokeh.io import export_png
from cStringIO import StringIO

from bokeh.io import export_svgs
from bokeh.io.export import get_svgs
from bokeh.io.export import get_screenshot_as_png
from bokeh.io.export import webdriver_control
from xvfbwrapper import Xvfb

import logging
_logger = logging.getLogger(__name__)

# CODE + PROJECT IS COMPATIBLE WITH ODOO 10.
class signage(models.Model):
    _name = 'signage.signage'
    _inherit = ['mail.thread']

    name = fields.Char(string='name')
    template_id = fields.Many2one(comodel_name='ir.ui.view')
    area_ids = fields.One2many(comodel_name='signage.area',inverse_name='signage_id')
    state = fields.Selection([('draft','Draft'),('open','Open'),('closed','Closed')])
    description = fields.Text(string='Description')
    token = fields.Char(string="Token", help="Token calculates from Action 'Calculate Token'. Without token, this signage will be public.")

    @api.multi
    def replace_non_ascii_chars(sentence):
        sentence = sentence.replace(u"ä","a")
        return sentence
  
    @api.multi
    def get_token(self):
        for signage in self:
            # ~ token = hashlib.sha1(u'%s%s' %(signage.name.replace(u"ä", "a"), datetime.datetime.now())).hexdigest()
            token = hashlib.sha1(u'%s%s' %( signage.name.replace_non_ascii_chars(), datetime.datetime.now())).hexdigest()
            signage.token = token
        return token


class signage_area(models.Model):
    _name = 'signage.area'

    name = fields.Char(string='name')
    signage_id = fields.Many2one(comodel_name='signage.signage',string="Signage")
    page_ids = fields.One2many(comodel_name="signage.area.page",inverse_name='area_id', string='Pages')
    last_page = fields.Many2one(comodel_name="signage.area.page", string='Last Page')
    limit = fields.Integer(string='limit')
    nbr_pages = fields.Integer(compute='_nbr_pages', string='Number of pages')
    page_nbr = fields.Integer(compute='_page_nbr', string='Page number')

    def _nbr_pages(self):
        self.nbr_pages = len(self.page_ids)

    def _page_nbr(self):
        if not self.last_page:
            self.page_nbr = 1
        else:
            for position, page in enumerate(self.page_ids,1):
                if page == self.last_page:
                    self.page_nbr = position
        self.page_nbr = len(self.page_ids)

    @api.multi
    def get_next_page(self):
        self.ensure_one()
        found, next = False, False
        for page in self.page_ids:
            if page == self.last_page:
                next = True
            elif next:
                self.last_page = page
                found = True
                break
        if not found and len(self.page_ids) > 0:
            self.last_page = self.page_ids[0]
        return self.last_page

    @api.multi
    def get_page_nbr(self, page):
        res = 1
        for p in self.page_ids:
            if page == p:
                return res
            res += 1


class signage_area_page(models.Model):
    _name = 'signage.area.page'

    name = fields.Char(string='Name')
    area_id = fields.Many2one(comodel_name='signage.area',string='Area')
    template_id = fields.Many2one(comodel_name='ir.ui.view', string='Template')
    offset = fields.Integer(string='Offset')
    limit = fields.Integer(string='Limit')

    def total_pages(self, lines):
        if self.limit != 0:
            return int(math.ceil(float(len(lines)) / float(self.limit)))
        else:
            return 1

    def current_page(self):
        if self.limit != 0:
            return self.offset / self.limit + 1
        else:
            return 1

    def offset_calc(self, lines):
        if (self.offset + self.limit) < len(lines):
            self.offset += self.limit
        else:
            self.offset = 0

    # template:
    # foreach mro in request.env['mro.order'].search([('xyz')],limit=10,offset=offset(0,10,20,30),order='name,date')
    # http://erikflowers.github.io/weather-icons/
    # http://opendata.smhi.se/apidocs/metfcst/index.html

class ir_ui_view(models.Model):
    _inherit = 'ir.ui.view'
    # ~ When back-office fail to upgrade a new column to database, then update by code:
    # ~ odooupdm {databasename} {module.name}
    # ~ odooupdm test3 signage
    number_of_areas = fields.Integer(string='Number of Areas')
    
    
class WebsiteSignage(http.Controller):
    # ORDER OF ROUTING:
    # 1. ROUTING (INDEX / SHOW) <--- ***
    # 2. INSERT
    # 3. UPDATE
    # 4. DELETE
    # 


    # SHOW + TOKEN
    #/signage/view/menu/{menu.name}/submenu.name/all?token=123
    @http.route(['/signage/<string:signage>/<string:area>'],type='http', auth='public', website=True)
    def signage_view_page(self, signage, area, **post): #return the last page from a specified area
        signage = request.env['signage.signage'].sudo().search([('name', '=', signage)])
        if signage:
            if signage.token and post.get('token') and signage.token == post.get('token'):
                area = request.env['signage.area'].sudo().search([('name', '=', area), ('signage_id', '=', signage.id)])
                if area:
                    return request.render(area.get_next_page().template_id.key, {'signage': signage,'area': area, 'page': area.last_page})
            else:
                return request.render('website.403', {})
        return False


    # ORDER OF ROUTING:
    # 1. ROUTING (INDEX / SHOW)
    # 2. INSERT <--- ***
    # 3. UPDATE
    # 4. DELETE

    # INSERT NEW AREA
    # SUBMENU = AREA
    # /signage/admin/submenu/insert
    @http.route(['/signage/admin/submenu/<string:signage>/insert'],type='http', auth='user', website=True)
    def signage_area_insert(self, signage, **post):
        signage = request.env['signage.signage'].search([('name','=',signage)])
        if signage :
            area = request.env['signage.area'].search([('name','=',area),('signage_id','=',signage.id)])
            # ~ page_name = '%s-%s-%s' % (signage.name, area.name,'p%s' % (area.nbr_pages + 1))
            area_name = '%s-%s' % (signage.name, area.name)
            xml_id = request.env['website'].new_page(page_name, template='website.signage_page_template')
            template = request.env['ir.ui.view'].search([('key','=',xml_id)])
            new_page = request.env['signage.area.page'].create({
                'area_id': area.id,
                'name': '%s_page_%s' % (area.name, area.nbr_pages + 1),
                'template_id': template.id,
             })
        return werkzeug.utils.redirect('/signage/%s/edit_area' %new_area.id)

    # ~ @http.route(['/signage/<string:signage>/<string:area>/editSubmenu'],type='http', auth='user', website=True)
    # ~ def signage_area_edit_submenu(self, signage, **post):

    # INSERT NEW PAGE 
    # 2019-01-28
    # POST = PAGE
    # /signage/admin/post/{menu.name}/{submenu.name}/insert   
    @http.route(['/signage/admin/post/<string:signage>/<string:area>/insert'],type='http', auth='user', csrf=False, website=True)
    def post_insert(self, signage, area=None, page=None, **post):
        _logger.warn('<<<<<<<<<<<<<<<<<  post %s' % post)
        signage = request.env['signage.signage'].search([('name','=',signage)])
        if signage and area:
            title = ""
            if post.get('title') == "":
                title = "page"
            else:
                title = post.get('title')

            #title = post.get('title', '%s_page_%s' % (area.name, area.nbr_pages + 1) )
            #_logger.warn('<<<<<<<<<<<<<<<<<  title %s' % title)
            area = request.env['signage.area'].search([('name','=',area),('signage_id','=',signage.id)])
            page_name = '%s-%s-%s' % (signage.name, area.name,'p%s' % (area.nbr_pages + 1))
            xml_id = request.env['website'].new_page(page_name, template='website.signage_page_template')
            template = request.env['ir.ui.view'].search([('key','=',xml_id)])
            new_page = request.env['signage.area.page'].create({
                'area_id': area.id,
                'name': ('%s_%s_%s' % (area.name, title, area.nbr_pages + 1) ),
                'template_id': template.id,
             })

            # /signage/admin/post/{id}/edit
            # REDIRECT >> EDIT NEW POST
            # return werkzeug.utils.redirect('/signage/admin/post/%s/edit' %new_page.id)
            # REDIRECT >> OVERVIEW
            # ~ if post.get('returnPath') == "signage-admin-menu-edit":
                # ~ return werkzeug.utils.redirect('/signage/admin/menu/%s/edit' % signage.id)
            # ~ elif:
                # ~ return werkzeug.utils.redirect('/signage/')
            # ~ else:
            if post.get("returnPath") == "signageAdminMenuEdit":
                return werkzeug.utils.redirect('/signage/admin/menu/%s/edit' % signage.id)
            elif post.get("returnPath") == "signage":
                return werkzeug.utils.redirect('/signage/admin/menu/%s/edit' % signage.id)
                # ~ return werkzeug.utils.redirect('/signage')
            # ~ else:
                # ~ return werkzeug.utils.redirect('/signage/admin/menu/%s/edit' % signage.id)



    # ORDER OF ROUTING:
    # 1. ROUTING (INDEX)
    # 2. INSERT
    # 3. UPDATE <--- *** 
    # 4. DELETE 


    # EDIT MENU >> TO ADD POSTS
    # **********************************
    # /signage/admin/menu/{menu.id}/edit
    @http.route(['/signage/admin/menu/<model("signage.signage"):signage>/edit'],type='http', auth='user', website=True)
    def signage_edit_signage(self, signage, **post): #return a specified page and activate edit mode
        area_list = []
        for area in signage.area_ids.sorted(lambda a: a.name):
            strText2 = ""
            # /signage/admin/post/{menu.name}/{area.name}/insert        
            strText3 = "<div><form action=\"/signage/admin/post/%s/%s/insert\" method=\"post\"> \n" % (signage.name, area.name)
            strText3 +="<input type=\"text\" size=\"10\" name=\"title\" /> \n" \
                + "<input type=\"hidden\" name=\"returnPath\" value=\"signageAdminMenuEdit\"> \n" \
                + "<input type=\"submit\" value=\"Add...\" /> \n" \
                + "</form></div>" + "\n"
            for page in area.page_ids:
                # FONTS AS ICONS
                # https://fontawesome.com/v4.7.0/cheatsheet/
                # UPDATE = fa-pencil
                # https://fontawesome.com/v4.7.0/icon/pencil
                # /signage/admin/post/{post.id}/edit
                strText2 += "<div><a href=\"/signage/admin/post/%s/edit/\" title=\"View / Edit post\" alt=\"View / Edit post\">" % (page.id)
                strText2 += "<i class=\"fa fa-pencil\" aria-hidden=\"true\"></i></a> %s" % (page.name) + "\n"

                # TRASH = fa-trash
                # https://fontawesome.com/v4.7.0/icon/trash
                # /[project]/admin/post/{menuId.id}/{post.id}/delete
                strText2 += " <a href=\"/signage/admin/post/%s/%s/delete\" title=\"Delete post\" alt=\"Delete post\"><i class=\"fa fa-trash\" aria-hidden=\"true\"></i></a></div>" % (signage.id, page.id) + "\n"
            
            # EDIT SUBMENU
            # /[project]/admin/submenu/{submenu.id}/edit
            # strText1 = "<a href=\"/signage/admin/submenu/%s/edit/\" title=\"View / Edit Signage Area\" alt=\"View / Edit Signage Area\"><i class=\"fa fa-pencil\" aria-hidden=\"true\"></i></a> %s" % (area.id, area.name) + "\n"
            # DELETE SUBMENU
            # ONLY DELETE IF THERE ARE 0 PAGES!! :-)
            # /[project]/admin/submenu/{submenu.id}/delete
            # strText1 += " <a href=\"/signage/admin/submenu/%s/delete/\" title=\"Delete Signage Area\" alt=\"Delete Signage Area\"><i class=\"fa fa-trash\" aria-hidden=\"true\"></i></a>" % (area.id) + "\n"
            
            # *************************************************

            area_list.append('%s id: %s <br />%s <br />%s' % (area.name, area.id, strText2, strText3))
            # area_list.append('%s <br />%s <br />%s' % (strText1, strText2, strText3))
                        
            #_logger.warn('<<<<<<<<<<<<<<<<<  area_list %s' % area_list)
            #_logger.warn('<<<<<<<<<<<<<<<<<  templatekey %s' % signage.template_id.key)
        return request.render(signage.template_id.key, {'signage': signage, 'area_list': area_list, 'hide_header': False, 'code_previous_page' : """        <div class="row">
          <div class="col-sm-4" />
          <div class="col-sm-4" style="text-align:center">
            <!--
                 # https://fontawesome.com/v4.7.0/icon/arrow-circle-left
            -->
            <h3>
              <a href="/signage/" title="Index" alt="Index">
                <i class="fa fa-arrow-circle-left fa-2x" aria-hidden="true" />
              </a>
              Edit Signage Templates
            </h3>
          </div>
          <div class="col-sm-4" />
        </div>
        """})


  

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
