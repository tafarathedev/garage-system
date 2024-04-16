from odoo import models, fields, api, _

class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    check_ids = fields.Many2many('maintenance.checklist',string='Maintenance CheckList')
    line_ids = fields.One2many('equipment.part.line','maintenance_equipment_id','line')
