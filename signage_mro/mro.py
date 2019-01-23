# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Enterprise Resource Management Solution, third party addon
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
from openerp import api, fields, models,_
from openerp import http
from openerp.http import request
from datetime import timedelta

import logging
_logger = logging.getLogger(__name__)

WEEK = 4

class mro_order(models.Model):
    _inherit = 'mro.order'

    @api.model
    def formatted_name(self, name):
        n_list = []
        if name:
            n_list = name.split(' ')
            if len(n_list) > 1:
                return ' '.join([n_list[0], n_list[1][:1]])
            else:
                return name
        else:
            return name

    @api.model
    def get_mro_by_station(self, limit, offset):
        weekdays = self.get_weekdays()
        mros = self.env['mro.order'].sudo().search([('state', '=', 'ready'), ('mechanician_id', '!=', 111), ('date_scheduled', '>=', weekdays[0]+' 00:00:00'), ('date_scheduled', '<=', weekdays[-1]+' 23:59:59')], limit=limit, offset=offset, order='workstation')
        if len(mros) > 0:
            stations = mros.mapped('workstation')
            if len(stations) >= offset:
                return {'stations': stations[offset:offset+limit] if len(stations) > offset else stations}
        return {'stations': []}

    @api.model
    def get_all_mro(self):
        weekdays = self.get_weekdays()
        return self.env['mro.order'].sudo().search([('workstation', '!=', 'false'), ('state', '=', 'ready'), ('mechanician_id', '!=', 111), ('date_scheduled', '>=', weekdays[0]+' 00:00:00'), ('date_scheduled', '<=', weekdays[-1]+' 23:59:59')])

    @api.model
    def get_station_mro(self, station):
        weekdays = self.get_weekdays()
        return self.env['mro.order'].sudo().search([('workstation', '=', station.id), ('state', '=', 'ready'), ('mechanician_id', '!=', 111), ('date_scheduled', '>=', weekdays[0]+' 00:00:00'), ('date_scheduled', '<=', weekdays[-1]+' 23:59:59')])

    @api.model
    def get_mechanician(self, limit, offset):
        weekdays = self.get_weekdays()
        mros = self.env['mro.order'].sudo().search([('state', 'in', ['released', 'ready']), ('mechanician_id', '!=', 111), ('date_scheduled', '>=', weekdays[0]+' 00:00:00'), ('date_scheduled', '<=', weekdays[-1]+' 23:59:59')])
        if len(mros) > 0:
            mechanicians = mros.mapped('mechanician_id')
            if len(mechanicians) >= offset:
                return {'mechanicians': mechanicians[offset:offset+limit] if len(mechanicians) > offset else mechanicians}
        return {'mechanicians': []}

    @api.model
    def get_weekdays(self):
        today = fields.Date.from_string(fields.Date.today())
        weekdays = [today + timedelta(days=i) for i in range(-WEEK*7 - today.weekday(), 7 - today.weekday())]
        start = weekdays[0]
        end = weekdays[-1]
        delta = timedelta(days=1)
        weekend = set([5,6])
        days = []
        d = start
        diff = 0
        while d <= end:
            if d.weekday() not in weekend:
                days.append(fields.Date.to_string(d))
                diff += 1
            d += delta
        return days

    @api.model
    def get_wd(self, days, i):
        return days[i::5]

    @api.model
    def get_mechanician_mro(self, mechanician, day):
        return self.env['mro.order'].sudo().search([('mechanician_id', '=', mechanician.id), ('date_scheduled', '>=', day), ('date_scheduled', '<', fields.Date.to_string(fields.Date.from_string(day) + timedelta(days=1)))])

    @api.model
    def get_mechanician_efficiency(self, mechanician, day):
        duration = sum(self.env['mro.order'].sudo().search([('mechanician_id', '=', mechanician.id), ('date_scheduled', '>=', day), ('date_scheduled', '<', fields.Date.to_string(fields.Date.from_string(day) + timedelta(days=1)))]).mapped('order_duration'))
        if duration >= 8.0:
            return 100
        else:
            procent = (duration/8.0)*100
            return procent if procent%1 != 0 else int(procent)

    @api.model
    def get_etd(self, date_scheduled, duration):
        dt_delivery = fields.Datetime.from_string(date_scheduled) + timedelta(hours=int(duration))
        if (fields.Date.to_string(dt_delivery)[:10] == fields.Date.today()[:10]):
            d = dt_delivery - fields.Datetime.from_string(fields.Datetime.now())
            #~ return '%s,%s' %(d.seconds/3600, (d.seconds%3600)/60)
            #~ return fields.Datetime.to_string(dt_delivery)[11:-3]
        return '%s/%s' %(fields.Datetime.to_string(dt_delivery)[8:10].strip('0'), fields.Datetime.to_string(dt_delivery)[5:7].strip('0'))
        #~ else:
            #~ return '%s/%s' %(fields.Datetime.to_string(dt_delivery)[8:10].strip('0'), fields.Datetime.to_string(dt_delivery)[5:7].strip('0'))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
