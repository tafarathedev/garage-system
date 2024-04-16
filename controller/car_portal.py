# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers import portal
import base64


class CarPortal(portal.CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        CarRepairObj = request.env['car.repair.request']
        if 'car_request_count' in counters:
            count = CarRepairObj.sudo().search([])
            values['car_request_count'] = len(count)

        return values

    @http.route(['/my/car'], type='http', auth="user", website=True)
    def portal_my_car_request(self):
        car_request = request.env['car.repair.request'].sudo().search([])
 
        values = {
            'default_url': "/my/car",
            'car_request': car_request,
            'page_name': 'car_request',
        }

        return request.render("car_repair_maintenance_axis.portal_my_car_requests",
                              values)


class PartnerForm(http.Controller):

    @http.route(['/car/form'], type='http', auth="public", website=True)
    def partner_form(self, **post):
        service_id = request.env['car.service'].sudo().search([])
        car_id = request.env['car'].sudo().search([])

        return request.render("car_repair_maintenance_axis.car_repair_template",
                              {'service_id': service_id,
                               'car_id': car_id, })

    @http.route(['/car/form/submit'], type='http', auth="public", website=True)
    def customer_form_submit(self, **post):

        partner = request.env['car.repair.request'].sudo().create({
            'name': post.get('name'),
            'email': post.get('email'),
            'phone': post.get('phone'),
            'reason_for_repair': post.get('reason_for_repair'),
            'car_id': post.get('car_id'),
            'car_brand': post.get('car_brand'),
            'service_id': post.get('service_id'),
            'reason_details': post.get('reason_details'),
            'list_of_damage': post.get('list_of_damage'),
            'priority': post.get('priority'),
        })
        vals = {
            'partner': partner,
        }
        return request.render("car_repair_maintenance_axis.car_repair_template_submit", vals)
