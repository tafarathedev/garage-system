from odoo import models, fields


class CarServiceTeam(models.Model):

    _name = 'car.service'
    _description = 'Car Service'

    name = fields.Char(string='Service Name', required=True)
    description = fields.Text(string='Description')
    price = fields.Float(string='Price')
    duration = fields.Integer(string='Duration in Minutes')
    service_type_id = fields.Many2one('car.service.type', string='Service Type')


class CarServiceType(models.Model):

    _name = 'car.service.type'
    _description = 'Car Service Type'

    name = fields.Char(string='Type Name', required=True)
    description = fields.Text(string='Description')
