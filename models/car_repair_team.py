from odoo import fields, models, api, _


class CarRepair(models.Model):
    _name = 'car.repair.team'

    name = fields.Char(string='Name')
    id_default_team = fields.Boolean(string='Is Default Team')
    leader_id = fields.Many2one('res.users', string='Leader')
    team_members_ids = fields.Many2many('res.users', string='Team Members')


class ResUsers(models.Model):
    _inherit = 'res.users'

    team_members_id = fields.Many2one("car.repair.team")
