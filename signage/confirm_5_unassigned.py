# confirm_5_unassigned.py
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


# GENERIC CODE FOR ROUTING
# 1. ROUTING (INDEX / SHOW)
# 2. INSERT
# 3. UPDATE
# 4. DELETE
# 5. UNASSIGNED / OTHER <--- ***
# CODE + PROJECT IS COMPATIBLE WITH ODOO 10.
class WebsiteSignage(http.Controller):

    ## DEMO
    @http.route(['/signage/view/demo'], type='http', auth='public', website=True)
    def signage_demo(self):
        return request.render('signage.signage_demo', {})

    ## DEMO
    @http.route(['/signage/view/demo1'], type='http', auth='public', website=True)
    def signage_demo1(self):
        f = open('/usr/share/odoo-signage/signage/static/src/img/archive.gif')
        gif = f.read()
        f.close()
        return http.send_file(StringIO(gif),mimetype='image/gif')

    ## DEMO
    @http.route(['/signage/view/demo3'], type='http', auth='public', website=True)
    def signage_demo1(self):
        fruits = ['Onsdag', 'Torsdag', 'Fredag', u'Måndag', 'Tisdag']
        counts = [55, 33, 44, 22, 44]

        source = ColumnDataSource(data=dict(fruits=fruits, counts=counts))

        p = figure(x_range=fruits, plot_height=350, toolbar_location=None, title="Order statistik")
        p.vbar(x='fruits', top='counts', width=0.9, source=source, legend="fruits",
               line_color='white', fill_color=factor_cmap('fruits', palette=Spectral6, factors=fruits))

        p.xgrid.grid_line_color = None
        p.y_range.start = 0
        p.y_range.end = 70
        p.legend.orientation = "horizontal"
        p.legend.location = "top_center"

        _logger.warn('<<<<<<<<<<<<<<<<<  p %s' % p)
        
        gif = p
        vdisplay = Xvfb()
        vdisplay.start()

        # launch stuff inside
        # virtual display here.
        png = get_screenshot_as_png(p, webdriver=webdriver_control.create())    
        _logger.warn('<<<<<<<<<<<<<<<<<  png %s' % png.tobytes(encoder_name='raw'))
        svg = get_svgs(p, webdriver=webdriver_control.create())    
        _logger.warn('<<<<<<<<<<<<<<<<<  svg %s' % svg)

        vdisplay.stop()
        return http.send_file(StringIO(svg),mimetype='image/svg-xml')        

    @http.route(['/signage_image/orders.svg'], type='http', auth='public', website=True)
    def signage_image_orders(self):
        fruits = ['Onsdag', 'Torsdag', 'Fredag', u'Måndag', 'Tisdag']
        counts = [55, 33, 44, 22, 44]

        source = ColumnDataSource(data=dict(fruits=fruits, counts=counts))

        p = figure(x_range=fruits, plot_height=350, toolbar_location=None, title="Order statistik")
        p.vbar(x='fruits', top='counts', width=0.9, source=source, legend="fruits",
               line_color='white', fill_color=factor_cmap('fruits', palette=Spectral6, factors=fruits))

        p.xgrid.grid_line_color = None
        p.y_range.start = 0
        p.y_range.end = 70
        p.legend.orientation = "horizontal"
        p.legend.location = "top_center"

        _logger.warn('<<<<<<<<<<<<<<<<<  p %s' % p)

        #show(p)
        #p.output_backend = "svg"
        #export_svgs(p, filename="plot.svg")
        #t = NamedTemporaryFile(suffix=".svg")
        #export_svgs(p, filename=t.name, webdriver=WebDriver())
        #t.write(p)
        #t.seek(0)
        #print(t.read())
        #t.close()
        
        vdisplay = Xvfb()
        vdisplay.start()

        # launch stuff inside
        # virtual display here.
        png = get_screenshot_as_png(p, webdriver=webdriver_control.create())    
        _logger.warn('<<<<<<<<<<<<<<<<<  png %s' % png)

        vdisplay.stop()

        # launch stuff inside virtual display here.
        # It starts/stops around this code block.

        # export_png(p, filename="plot.png")
        # p.output_backend = "svg"
        return http.send_file(StringIO(png),mimetype='image/png')
