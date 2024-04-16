from odoo import models, fields


class JobRoles(models.Model):
    _name = 'job.roles'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string="Description")


class ResUsers(models.Model):
    _inherit = 'res.users'

    job_roles_ids = fields.Many2many('job.roles', string='Job Roles')
    # is_technician = fields.Boolean(string="Is Technician", compute="_compute_job_roles")
    # is_manager = fields.Boolean(string="Is Manager", compute="_compute_job_roles")
    # is_admin = fields.Boolean(string="Is Admin", compute="_compute_job_roles")
    # is_worker = fields.Boolean(string="Is Worker", compute="_compute_job_roles")
    #
    # @api.depends('job_roles_ids')
    # def _compute_job_roles(self):
    #     for user in self:
    #         user.is_technician = any(job_role.name == 'Technician' for job_role in user.job_roles_ids)
    #         user.is_manager = any(job_role.name == 'Manager' for job_role in user.job_roles_ids)
    #         user.is_admin = any(job_role.name == 'Admin' for job_role in user.job_roles_ids)
    #         user.is_worker = any(job_role.name == 'Worker' for job_role in user.job_roles_ids)