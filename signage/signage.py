﻿# -*- coding: utf-8 -*-
##############################################################################
#
# Odoo, Open Source Enterprise Resource Management Solution, third party addon
# Copyright (C) 2017- Vertel AB (<http://vertel.se>).
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
import math
import werkzeug
from werkzeug.exceptions import NotFound

import logging
_logger = logging.getLogger(__name__)


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
    def get_token(self):
        token = hashlib.sha1('%s%s' %(self.name, datetime.datetime.now())).hexdigest()
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


class WebsiteSignage(http.Controller):

    @http.route(['/signage','/signage/list'],type='http', auth='user', website=True)
    def signage_list(self, **post):
        return request.render('signage.signage_list', {'signages': request.env['signage.signage'].search([('state','=','open')])})

    @http.route(['/signage/overview'],type='http', auth='user', website=True)
    def signage_overview(self, **post):
        return request.render('signage.signage_overview', {'signages': request.env['signage.signage'].search([('state','=','open')])})

    @http.route(['/signage/<string:signage>/<string:area>'],type='http', auth='public', website=True)
    def signage_view_page(self, signage, area, **post): #return the last page from a specified area
        signage = request.env['signage.signage'].sudo().search([('name', '=', signage)])
        if signage:
            if signage.token and post.get('token') and signage.token == post.get('token'):
                area = request.env['signage.area'].sudo().search([('name', '=', area), ('signage_id', '=', signage.id)])
                if area:
                    return request.render(area.get_next_page().template_id.key, {'signage': signage, 'area': area, 'page': area.last_page})
            else:
                return request.render('website.403', {})
        return False

    @http.route(['/signage/<model("signage.area.page"):page>/edit'],type='http', auth='user', website=True)
    def signage_edit_page(self, page, **post): #return a specified page and activate edit mode
        return request.render(page.template_id.key, {'signage': page.area_id.signage_id, 'area': page.area_id, 'page': page, 'edit': True})

    @http.route(['/signage/<string:signage>/<string:area>/new'],type='http', auth='user', website=True)
    def signage_page_edit(self, signage, area=None,page=None, **post):
        signage = request.env['signage.signage'].search([('name','=',signage)])
        if signage and area:
            area = request.env['signage.area'].search([('name','=',area),('signage_id','=',signage.id)])
            page_name = '%s-%s-%s' % (signage.name, area.name,'p%s' % (area.nbr_pages + 1))
            xml_id = request.env['website'].new_page(page_name, template='website.signage_page_template')
            template = request.env['ir.ui.view'].search([('key','=',xml_id)])
            new_page = request.env['signage.area.page'].create({
                'area_id': area.id,
                'name': '%s_page_%s' % (area.name, area.nbr_pages + 1),
                'template_id': template.id,
             })
            return werkzeug.utils.redirect('/signage/%s/edit' %new_page.id)

    @http.route(['/signage/demo'], type='http', auth='public', website=True)
    def signage_demo(self):
        return request.render('signage.signage_demo', {})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
