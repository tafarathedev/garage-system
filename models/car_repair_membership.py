from odoo import fields, models, api, _


class CarServicingMembership(models.Model):
    _name = 'car.servicing.membership'
    _description = 'Car Servicing Membership'

    name = fields.Char(string='Membership Number')
    validity_period = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('half_yearly', 'Half Yearly'),
        ('yearly', 'Yearly')
    ], 'Validity Period')
    customer = fields.Many2one('res.partner', string='Customer', required=True)
    car_id = fields.Many2one('car', string='Car', domain="[('owner_id', '=', customer)]", required=True, create=True)
    membership_beginning_date = fields.Date(string='Beginning Date')
    membership_expiration_date = fields.Date(string='Expiration Date')
    notes = fields.Text('Notes')
    amount = fields.Float('Amount')
    membership_plan = fields.Many2one('membership.plan', string='Membership Plan')
    services = fields.Many2many('service.option', string='Services')

    @api.onchange('membership_plan')
    def _onchange_membership_plan(self):
        self.amount = self.membership_plan.price
        self.services = self.membership_plan.services

    @api.model
    def create(self, vals):
        membership = super(CarServicingMembership, self).create(vals)
        if membership.membership_plan:
            membership.amount = membership.membership_plan.price
            membership.services = membership.membership_plan.services
        return membership


class MembershipPlan(models.Model):
    _name = 'membership.plan'
    _description = 'Membership Plan'

    name = fields.Char(string='Plan Name')
    description = fields.Text(string='Description')
    price = fields.Float(string='Price')
    services = fields.Many2many('service.option', string='Services Included')


class ServiceOption(models.Model):
    _name = 'service.option'
    _description = 'Service Option'

    name = fields.Char(string='Service Name')
    description = fields.Text(string='Description')
    price = fields.Float(string='Price')
