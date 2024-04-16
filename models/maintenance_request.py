from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import calendar as cal


class HrEquipmentStage(models.Model):
    _inherit = 'maintenance.stage'

    status = fields.Char(string='Status', translate=False)

    @api.onchange('name')
    def onchange_state(self):
        self.status = self.name

class HrEquipmentRequest(models.Model):
    _inherit = 'maintenance.request'
    _order = "priority desc, id desc"

    state = fields.Selection([('new', 'New Request'),
                              ('in_progress', 'In Progress'),
                              ('repair', 'Repaired'),
                              ('scrap', 'Scrap')], default='new', string='Status', translate=False)
    location_id = fields.Many2one('stock.location', 'Destination Location')
    desc = fields.Char('Description')
    checklist_ids = fields.One2many('maintenance.checklist', 'maintenance_id', 'Check')
    checklist_line_ids = fields.One2many('maintenance.checklist.line', 'maintenance_id', "CheckList Lines")
    product_id = fields.Many2one('product.product', 'Product')
    qty = fields.Float('Quantity')
    uom_id = fields.Many2one('uom.uom', 'UOM')
    equipment_ids = fields.One2many('equipment.part.line', 'maintenance_id', string='Eqipment')
    project_task_id = fields.Many2one('project.task', "Job Order")
    is_project_task = fields.Boolean('Is Job Order ?', default=False, copy=False)
    is_material_requisition = fields.Boolean('Is Material Requisition?', default=False, copy=False)
    partner_req_vendor_id = fields.Many2one('res.partner', 'Equipment Purchase Requisition Vendor')
    priority = fields.Selection(
        [('0', 'Very Low'), ('1', 'Low'), ('2', 'Normal'), ('3', 'High')],
        default='0', index=True, string="Priority")

    def check_validation(self):
        for rec in self:
            if not rec.schedule_date:
                raise UserError(_('Please Select Scheduled Date.'))
            if not rec.equipment_ids:
                raise UserError(_('Please Select Equipment Material Line.'))
            if not rec.location_id:
                raise UserError(_('Please Select Destination Location.'))
            if not rec.partner_req_vendor_id:
                raise UserError(_('Please Select Equipment Purchase Requisition Vendor.'))

    def create_job_order(self):
        for rec in self:
            task_vals = {
                'name': rec.name,
                'description': rec.description,
                'user_ids': [(6,0, [rec.user_id.id])],
                'is_order': True,
            }
            task = self.env['project.task'].create(task_vals)

            rec.project_task_id = task
            task.write({'maintenance_id': rec.id})
            rec.is_project_task = True
        self.display_job_order()

    def display_job_order(self):

        res = self.env.ref('car_repair_maintenance_axis.job_action')

        res = res.read()[0]
        res['domain'] = str([('maintenance_id', '=', self.id)])
        res['context'] = {
            'default_maintenance_id': self.id,
        }
        return res

    def create_purchase_requisition(self):
        for rec in self:
            self.check_validation()
            req_type = self.env['purchase.requisition.type'].search([('name', '=', 'Maintenance')])
            if not req_type:
                req_type = self.env['purchase.requisition.type'].create({
                    'name': 'Maintenance',
                    'quantity_copy': 'none'
                })
            for line in rec.equipment_ids:
                line_vals = (0, 0, {
                    'product_id': line.product_id.id,
                    'product_qty': line.qty,
                    'price_unit': line.product_id.standard_price,
                    'schedule_date': rec.schedule_date,
                })
            purchase_requisition_vals = {
                'user_id': rec.user_id.id,
                'type_id': req_type.id,
                'ordering_date': fields.Datetime.now(),
                'description': rec.description,
                'maintenance_id': rec.id,
                'schedule_date': rec.schedule_date,
                'vendor_id': rec.partner_req_vendor_id.id,
                'line_ids': [(0, 0, {
                    'product_id': line.product_id.id,
                    'product_qty': line.qty,
                    'price_unit': line.product_id.standard_price,
                    'schedule_date': rec.schedule_date,
                }) for line in rec.equipment_ids],
            }

            material_requisition = self.env['purchase.requisition'].create(
                purchase_requisition_vals)
            rec.is_material_requisition = True
        self.display_purchase_requisition()

    def display_purchase_requisition(self):
        res = self.env.ref('car_repair_maintenance_axis.action_purchase_requisition')
        res = res.read()[0]
        res['domain'] = str([('maintenance_id', '=', self.id)])
        return res

    def write(self, vals):
        res = super(HrEquipmentRequest, self).write(vals)
        for request_id in self:
            if vals.get('equipment_id', False):

                equipment_data = self.env['maintenance.equipment'].browse(vals['equipment_id'])

                for check_id in equipment_data.check_ids:
                    checklist_vals = {
                        'name': check_id.name,
                        'desc': check_id.desc,
                        'maintenance_id': request_id.id,
                    }
                    self.env['maintenance.checklist.line'].create(checklist_vals)
                for line_id in equipment_data.line_ids:
                    equipment_part_line_vals = {
                        'product_id': line_id.product_id.id,
                        'qty': line_id.qty,
                        'uom_id': line_id.uom_id.id,
                        'maintenance_id': request_id.id,
                    }
                    self.env['equipment.part.line'].create(equipment_part_line_vals)
        return res

    @api.model
    def create(self, vals):
        request_id = super(HrEquipmentRequest, self).create(vals)
        if vals.get('equipment_id', False):

            equipment_data = self.env['maintenance.equipment'].browse(vals['equipment_id'])

            for check_id in equipment_data.check_ids:
                checklist_vals = {
                    'name': check_id.name,
                    'desc': check_id.desc,
                    'maintenance_id': request_id.id,
                }
                self.env['maintenance.checklist.line'].create(checklist_vals)
            for line_id in equipment_data.line_ids:
                equipment_part_line_vals = {
                    'product_id': line_id.product_id.id,
                    'qty': line_id.qty,
                    'uom_id': line_id.uom_id.id,
                    'maintenance_id': request_id.id,
                }
                self.env['equipment.part.line'].create(equipment_part_line_vals)
        return request_id

    @api.model
    def get_count_list(self):
        stage_data = self.env['maintenance.stage'].search([('name', '=', 'New Request')])
        request_data = self.env['maintenance.request'].search([('stage_id', '=', stage_data.id)]).ids
        calculate_stage = len(request_data)

        stage_in_progress = self.env['maintenance.stage'].search([('name', '=', 'In Progress')])
        request_in_progress = self.env['maintenance.request'].search([('stage_id', '=', stage_in_progress.id)]).ids
        calculate_in_progress = len(request_in_progress)
        stage_in_repaired = self.env['maintenance.stage'].search([('name', '=', 'Repaired')])
        request_in_repaired = self.env['maintenance.request'].search([('stage_id', '=', stage_in_repaired.id)]).ids
        calculate_in_repaired = len(request_in_repaired)

        stage_in_scrap = self.env['maintenance.stage'].search([('name', '=', 'Scrap')])
        request_in_scrap = self.env['maintenance.request'].search([('stage_id', '=', stage_in_scrap.id)]).ids
        calculate_in_scrap = len(request_in_scrap)

        return {
            'calculate_stage': calculate_stage,
            'calculate_in_progress': calculate_in_progress,
            'calculate_in_repaired': calculate_in_repaired,
            'calculate_in_scrap': calculate_in_scrap,
        }

    @api.model
    def get_purchase_requision_data(self):
        cr = self._cr

        query = """
	       SELECT cl.request_date AS date_time,count(*) as count
	       FROM maintenance_request cl 
	       group by cl.request_date
	       order by cl.request_date

	       """
        cr.execute(query)
        partner_data = cr.dictfetchall()
        partner_day = []
        data_set = {}
        mycount = []
        list_value = []

        dict = {}
        count = 0

        months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
                  'August', 'September', 'October', 'November', 'December']

        for data in partner_data:
            if data['date_time']:
                mydate = data['date_time'].month
                for month_idx in range(0, 13):
                    if mydate == month_idx:
                        value = cal.month_name[month_idx]
                        list_value.append(value)
                        list_value1 = list(set(list_value))
                        for record in list_value1:
                            count = 0
                            for rec in list_value:
                                if rec == record:
                                    count = count + 1
                                dict.update({record: count})
                        keys, values = zip(*dict.items())
                        data_set.update({"data": dict})
        return data_set

