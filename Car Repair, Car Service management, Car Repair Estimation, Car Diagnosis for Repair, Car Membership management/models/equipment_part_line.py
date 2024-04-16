from odoo import models, fields, api, _

class EquipmentPartLine(models.Model):
	_name = 'equipment.part.line'


	product_id = fields.Many2one('product.product','product')
	qty = fields.Float('Quantity')
	uom_id = fields.Many2one('uom.uom','UOM')
	maintenance_equipment_id = fields.Many2one('maintenance.equipment','Equipment')
	maintenance_id = fields.Many2one('maintenance.request', 'Maintenance Request')


	@api.onchange('product_id')
	def onchange_product_data(self):
		for part_line_id in self:
			part_line_id.uom_id = part_line_id.product_id.uom_id


