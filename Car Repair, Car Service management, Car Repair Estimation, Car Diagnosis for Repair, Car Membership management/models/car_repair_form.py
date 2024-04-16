import calendar as cal

from odoo import fields, models, api, _


class CarRepair(models.Model):
    _name = 'car.repair.form'
    _description = 'Car Repair Form'

    name = fields.Char(string='Reference', default=lambda self: self.env['ir.sequence'].next_by_code('car.repair.form'))
    customer = fields.Many2one('res.partner', string='Customer', required=True)
    mobile = fields.Char(related='customer.mobile', string='Mobile Number', readonly=True)
    email = fields.Char(related='customer.email', string='Email', readonly=True)
    membership_id = fields.Many2one('car.servicing.membership', string='Membership Number', domain="[('customer', '=', customer)]")
    car_id = fields.Many2one('car', string='Car', domain="[('owner_id', '=', customer)]", required=True, create=True)
    brand = fields.Char(related='car_id.brand', string='Brand', readonly=True)
    model = fields.Char(related='car_id.model', string='Model', readonly=True)
    fuel_type = fields.Selection(related='car_id.fuel_type', string='Fuel Type', readonly=True,
                                 selection=[('petrol', 'Petrol'), ('diesel', 'Diesel'), ('hybrid', 'Hybrid'),
                                            ('electric', 'Electric')])
    color = fields.Char(related='car_id.color', string='Color', readonly=True)
    user_id = fields.Many2one('res.users', string='Technician', default=lambda self: self.env.user)
    repair_date = fields.Date(string='Repair Date')
    repair_notes = fields.Text(string='Repair Notes')
    project_id = fields.Many2one('project.project', string='Project')
    task_ids = fields.One2many('project.task', 'car_repair_id', string='Tasks')
    timesheet_ids = fields.One2many('account.analytic.line', 'car_repair_timesheet_id', string='Timesheet')
    checklist_ids = fields.Many2many('maintenance.checklist', string='Checklists')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('received', 'Received'),
        ('diagnosis', 'In Diagnosis'),
        ('progress', 'Work in Progress'),
        ('done', 'Done')
    ], string='Status', default='draft')
    diagnosis_count = fields.Integer(string='Diagnosis Count', compute='_compute_diagnosis_count')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order')
    diagnosis_id = fields.Many2one('car.repair.diagnosis', string='Diagnosis')
    date_received = fields.Date(string='Received Date')
    priority = fields.Selection([("0", ("Low")), ("1", ("Medium")), ("2", ("High")), ("3", ("Very High"))],
                                string="Priority", default="1")
    estimate_count = fields.Integer(string='Estimate Count')
    service_id = fields.Many2one('car.service', string='Car Service')
    car_repair_request_id = fields.Many2one('car.repair.request', string='Car Repair Request')

    # quotation_count = fields.Integer(string='Quotation Count', compute='_compute_quotation_count')

    # @api.depends('car_id')
    # def _compute_quotation_count(self):
    #     for diagnosis in self:
    #         quotation_count = self.env['sale.order'].search_count([('diagnosis_id', '=', diagnosis.id)])
    #         diagnosis.quotation_count = quotation_count

    @api.onchange('customer')
    def _onchange_customer(self):
        if self.customer:
            membership = self.env['car.servicing.membership'].search([('customer', '=', self.customer.id)], limit=1)
            if membership:
                self.membership_id = membership.id
            else:
                self.membership_id = False

    def create_membership(self):
        membership_vals = {
            'customer': self.customer.id,
            # Add other necessary fields for the membership
        }
        membership = self.env['car.servicing.membership'].create(membership_vals)
        self.membership_id = membership.id

    @api.depends('customer')
    def _compute_membership_id(self):
        for record in self:
            if record.is_package_zone_member:
                membership = self.env['car.servicing.membership'].search([('customer', '=', record.customer.id)],
                                                                         limit=1)
                record.membership_id = membership.id
            else:
                record.membership_id = False

    def create_sale_order(self):
        sale_order_vals = {
            'partner_id': self.customer.id,
            'order_line': [(0, 0, {
                'product_id': self.car_id.product_id.id,
                'name': self.car_id.name,
                'product_uom_qty': 1,
                'price_unit': self.car_id.list_price,
                'tax_id': [(6, 0, self.car_id.product_id.taxes_id.ids)],
            })]
        }
        sale_order = self.env['sale.order'].create(sale_order_vals)
        self.write({'sale_order_id': sale_order.id})
        return {
            'name': _('Sale Order'),
            'view_mode': 'form',
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'res_id': sale_order.id,
            'target': 'current',
        }

    def action_confirm_quotation(self):
        res = super().action_confirm_quotation()
        self.create_sale_order()
        return res

    def action_receive(self):
        self.write({'state': 'received'})

    def action_progress(self):
        self.write({'state': 'progress'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_print_repair_receipt_report(self):
        return self.env.ref('car_repair_maintenance_axis.action_car_repair_receipt_print').report_action(self)

    def action_print_repair_label_report(self):
        return self.env.ref('car_repair_maintenance_axis.action_car_repair_label_print').report_action(self)

    def action_print_repair_checklist(self):
        return self.env.ref('car_repair_maintenance_axis.action_car_repair_checklists_print').report_action(self)

    @api.onchange('project_id')
    def _onchange_project_id(self):
        task_ids = self.env['project.task'].search([('project_id', '=', self.project_id.id)])
        self.task_ids = task_ids

    def create_diagnosis(self):
        self.ensure_one()
        # if not self.diagnosis:
        #     raise UserError(_("Please enter Diagnosis."))
        diagnosis = self.env['car.repair.diagnosis'].create({
            'repair_id': self.repair_id.id,
            'diagnosis': self.diagnosis,
            'estimated_cost': self.estimated_cost,
        })
        diagnosis.update({'service_details': [(0, 0, {'name': 'Service Name 1', 'hours': 2}),
                                              (0, 0, {'name': 'Service Name 2', 'hours': 3})]})
        diagnosis.update({'checklist_ids': [(4, 1)]})
        view = self.env.ref('car_repair_maintenance_axis.view_car_repair_diagnosis_form')
        return {
            'name': _('Create Diagnosis'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'car.repair.diagnosis',
            'type': 'ir.actions.act_window',
            'res_id': diagnosis.id,
            'view_id': view.id,
            'target': 'new',
            'context': self.env.context,
        }

    def action_create_diagnosis(self):
        self.write({'state': 'diagnosis'})
        return {
            'name': 'Car Diagnosis Form',
            'view_mode': 'form',
            'res_model': 'car.repair.diagnosis',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_car_id': self.car_id.id, 'default_customer': self.customer.id, 'default_repair_id': self.id}
        }

    @api.depends('car_id')
    def _compute_diagnosis_count(self):
        for order in self:
            diagnosis_count = self.env['car.repair.diagnosis'].search_count([('car_id', '=', order.car_id.id)])
            order.diagnosis_count = diagnosis_count

    def show_diagnosis(self):
        return {
            'name': _('Diagnoses'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'car.repair.diagnosis',
            'type': 'ir.actions.act_window',
            'domain': [('car_id', '=', self.car_id.id)],
        }

    @api.model
    def get_car_repair_count_list(self):
        stage_data = self.env['car.repair.form'].search([('state', '=', 'received')])
        received_count = len(stage_data)
        in_diagnosis_data = self.env['car.repair.form'].search([('state', '=', 'diagnosis')])
        in_diagnosis_count = len(in_diagnosis_data)
        in_progress_data = self.env['car.repair.form'].search([('state', '=', 'progress')])
        in_progress_count = len(in_progress_data)
        done_data = self.env['car.repair.form'].search([('state', '=', 'done')])
        done_count = len(done_data)
        return {
            'received_count': received_count,
            'in_diagnosis_count': in_diagnosis_count,
            'in_progress_count': in_progress_count,
            'done_count': done_count,
        }

    def action_create_estimate(self):
        return {
            'name': 'Car Repair Estimate',
            'view_mode': 'form',
            'res_model': 'car.repair.estimate',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_car_repair_id': self.id}
        }

    def show_estimates(self):
        return {
            'name': _('Estimates'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'car.repair.estimate',
            'type': 'ir.actions.act_window',
            'domain': [('car_repair_id', '=', self.id)],
        }

    def show_quotations(self):
        return {
            'name': _('Quotations'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'domain': [('car_id', '=', self.car_id.id)],
        }

    @api.model
    def get_car_repair_week_data(self):
        cr = self._cr

        query = """
                  SELECT date_received AS date_received,count(*) as count
                  FROM car_repair_form
                  WHERE state = 'diagnosis' and date_received is not null
                    group by date_received
    	       order by date_received
                  """
        cr.execute(query)
        partner_data = cr.dictfetchall()
        data_set = {}
        mydate = []
        mycount = []
        list_value = []
        dict = {}
        count = 0
        days = ["Monday", "Tuesday", "Wednesday", "Thursday",
                "Friday", "Saturday", "Sunday"]
        for data in partner_data:
            if data['date_received']:
                mydate = data['date_received'].weekday()
                if mydate >= 0:
                    value = days[mydate]
                    list_value.append(value)

                    list_value1 = list(set(list_value))

                    for record in list_value1:
                        count = 0
                        for rec in list_value:
                            if rec == record:
                                count = count + 1
                            dict.update({record: count})
                        keys, values = zip(*dict.items())
                        # dict.update({'record': data['count_data'], 'day': value})
                        data_set.update({"data": dict})
        return data_set

    @api.model
    def get_car_repair_statistics_data(self):
        cr = self._cr

        query = """
    	       SELECT cl.repair_date AS date_time,count(*) as count
    	       FROM car_repair_form cl 
    	       group by cl.repair_date
    	       order by cl.repair_date

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

    # @api.depends('car_id')
    # def _compute_estimate_count(self):
    #     for order in self:
    #         estimate_count = self.env['car.repair.estimate'].search_count(
    #             [('car_repair_id.car', '=', order.car_id.id)])
    #         order.estimate_count = estimate_count


class CarRepairEstimate(models.Model):
    _name = 'car.repair.estimate'
    _description = 'Car Repair Estimate'
    _order = 'id desc'

    name = fields.Char(string='Estimate Number', default=lambda self: self.env['ir.sequence'].next_by_code('car.repair.estimate.sequence'))
    display_name = fields.Char(string='Display Name', required=True)
    car_repair_id = fields.Many2one('car.repair', string='Car Repair')
    description = fields.Text(string='Description')
    cost = fields.Float(string='Parts Cost', compute='_compute_total_cost', store=True)
    time = fields.Float(string='Time In Mins.')
    parts_required = fields.Many2many('product.product', string='Parts Required')
    total_cost = fields.Float(string='Total', compute='_compute_total_cost')

    @api.depends('parts_required.lst_price')
    def _compute_total_cost(self):
        for estimate in self:
            total_cost = sum(estimate.parts_required.mapped('lst_price'))
            estimate.total_cost = total_cost
            estimate.cost = total_cost

    def action_print_car_repair_estimate(self):
        return self.env.ref('car_repair_maintenance_axis.action_car_diagnosis_request_print').report_action(self)


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    car_repair_timesheet_id = fields.Many2one('car.repair.form', string='Task')


class ProjectTask(models.Model):
    _inherit = 'project.task'

    car_repair_id = fields.Many2one('car.repair.form', string='Car Repair')


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    diagnosis_id = fields.Many2one('car.repair.diagnosis', string='Diagnosis')

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            # Create a work order for each confirmed sale order line
            picking_type_id = self.env.ref('stock.picking_type_out').id
            # create picking
            picking = self.env["stock.picking"].create(
            {
                'picking_type_id': picking_type_id,
                'partner_id': order.partner_id.id,
                'origin': order.name,
                'location_dest_id': order.warehouse_id.lot_stock_id.id,
                'location_id': order.partner_id.property_stock_customer.id,
                'move_type': 'direct',
                'company_id': order.company_id.id,
                'sale_id': order.id,
                'note': order.note,
                'scheduled_date': fields.Date.today(),
                'priority': '0',
                'work_order_id': order.id,
            })
            for line in order.order_line:
                if line.product_id.type == 'product':
                        picking.write(
                            {
                                "move_ids": [
                                    (
                                        0,
                                        0,
                                        {
                                            'name': '/',
                                            'product_id': line.product_id.id,
                                            'product_uom': line.product_id.uom_id.id,
                                            'product_uom_qty': line.product_uom_qty,
                                            'location_dest_id': order.warehouse_id.lot_stock_id.id,
                                            'location_id': order.partner_id.property_stock_customer.id,
                                        },
                                    ),
                                ]
                            }
                        )
                picking.action_confirm()
                picking.action_assign()
        return res


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    work_order_id = fields.Many2one('mrp.workorder', string='Work Order')
    product_uom_qty = fields.Float(string='Quantity')


class CarRepairDiagnosis(models.Model):
    _name = 'car.repair.diagnosis'
    _description = 'Car Repair Diagnosis'

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: self.env['ir.sequence'].next_by_code('car.repair.diagnosis') or _('New'))
    subject = fields.Char(string='Subject', requried=True)
    customer = fields.Many2one('res.partner', string='Customer', required=True)
    mobile = fields.Char(related='customer.mobile', string='Mobile Number', readonly=True)
    email = fields.Char(related='customer.email', string='Email', readonly=True)
    car_id = fields.Many2one('car', string='Car', domain="[('owner_id', '=', customer)]", required=True, create=True)
    brand = fields.Char(related='car_id.brand', string='Brand', readonly=True)
    model = fields.Char(related='car_id.model', string='Model', readonly=True)
    car_number = fields.Char(related='car_id.car_num', string='Car Number', readonly=True)
    fuel_type = fields.Selection(related='car_id.fuel_type', string='Fuel Type', readonly=True)
    description = fields.Text(string='Diagnosis Description')
    user_id = fields.Many2one('res.users', string='Technician', default=lambda self: self.env.user)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done')
    ], string='Status', default='draft', readonly=True)
    date_confirmed = fields.Datetime(string='Date Confirmed', readonly=True)
    date_done = fields.Datetime(string='Date Done', readonly=True)
    checklist_ids = fields.Many2many('maintenance.checklist', string='Checklists')
    guarantee = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], string='Under Guarantee')
    guarantee_type = fields.Selection([
        ('free', 'Free'),
        ('paid', 'Paid'),
        ('hybrid', 'Hybrid')], string='Guarantee Type')
    service_nature = fields.Selection([
        ('full_service', 'Full Service'),
        ('partial_service', 'Partial Service'),
        ('custom_service', 'Custom Service')], string='Service Nature')
    appointment_date = fields.Date(string='Appointment Date')
    estimated_hours = fields.Float(string='Estimated Hours')
    service_charges = fields.Float(string='Servicing Charges')
    notes = fields.Text(string='Diagnostic Results')
    diagnosis_line_ids = fields.One2many('car.repair.diagnosis.line', 'diagnosis_id', string='Repair Lines')
    quotation_count = fields.Integer(string='Quotation Count', compute='_compute_quotation_count')
    repair_order_count = fields.Integer(string='Repair Order Count', compute='_compute_repair_order_count')
    work_order_count = fields.Integer(string='Work Orders', compute='_compute_work_order_count')
    work_order_id = fields.Many2one('work.order', string='Work Order')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('car.repair.diagnosis') or _('New')
        return super(CarRepairDiagnosis, self).create(vals)

    def action_confirm(self):
        self.write({'state': 'confirmed', 'date_confirmed': fields.Datetime.now(), 'user_id': self.env.user.id})

    def action_done(self):
        self.write({'state': 'done', 'date_done': fields.Datetime.now(), 'user_id': self.env.user.id})

    def action_print_diagnosis_request(self):
        return self.env.ref('car_repair_maintenance_axis.action_car_diagnosis_request_print').report_action(self)

    def action_car_diagnosis_result(self):
        return self.env.ref('car_repair_maintenance_axis.action_car_diagnosis_result_print').report_action(self)

    @api.onchange('owner_id')
    def _onchange_owner_id(self):
        car_ids = self.env['car'].search([('owner_id', '=', self.customer.id)])
        return {'domain': {'car_id': [('id', 'in', car_ids.ids)]}}

    def create_quotation(self):
        for rec in self:               
            order_vals = {
                'partner_id': rec.customer.id,
                'diagnosis_id': rec.id,
            }
            for line in rec.diagnosis_line_ids:
                order_vals['order_line'].append((0, 0, {
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.quantity,
                    'price_unit': line.unit_price,
                    'name': line.product_id.name,
                }))

            order_id = self.env['sale.order'].create(order_vals)
            return {
                'name': _('Sale Order'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'sale.order',
                'res_id': order_id.id,
                'type': 'ir.actions.act_window',
                'target': 'current',
            }

    @api.depends('car_id')
    def _compute_quotation_count(self):
        for diagnosis in self:
            quotation_count = self.env['sale.order'].search_count([('diagnosis_id', '=', diagnosis.id)])
            diagnosis.quotation_count = quotation_count

    def show_quotations(self):
        return {
            'name': _('Quotations'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'domain': [('diagnosis_id', '=', self.id)],
        }

    @api.depends('car_id')
    def _compute_repair_order_count(self):
        for diagnosis in self:
            count = self.env['car.repair.form'].search_count([('car_id', '=', diagnosis.car_id.id)])
            diagnosis.repair_order_count = count

    def show_repair_orders(self):
        return {
            'name': _('Repair Orders'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'car.repair.form',
            'type': 'ir.actions.act_window',
            'domain': [('car_id', '=', self.car_id.id)],
        }

    def create_work_order(self):
        work_order_obj = self.env['work.order']
        work_order_vals = {
            'customer_name': self.car_id.owner_id.name,
            'car_repair_diagnosis_id': self.id,
            'service_details': self.description,
            'service_date': self.appointment_date,
            'scheduled_date_planned': self.appointment_date,
        }
        work_order = work_order_obj.create(work_order_vals)
        return {
            'name': _('Work Order'),
            'type': 'ir.actions.act_window',
            'res_model': 'work.order',
            'view_mode': 'form',
            'res_id': work_order.id,
            'target': 'current',
        }

    @api.depends('car_id')
    def _compute_work_order_count(self):
        for diagnosis in self:
            work_order_count = self.env['work.order'].search_count([('car_repair_diagnosis_id', '=', diagnosis.id)])
            diagnosis.work_order_count = work_order_count

    def show_work_orders(self):
        return {
            'name': _('Work Orders'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'work.order',
            'type': 'ir.actions.act_window',
            'domain': [('car_repair_diagnosis_id', '=', self.id)],
        }


class CarRepairDiagnosisLine(models.Model):
    _name = 'car.repair.diagnosis.line'

    diagnosis_id = fields.Many2one('car.repair.diagnosis', string='Diagnosis')
    name = fields.Char(string='Description')
    product_id = fields.Many2one('product.product', string='Product')
    product_code = fields.Char(related='product_id.default_code', string='Product Code')
    quantity = fields.Float(string='Quantity')
    unit_price = fields.Float(related='product_id.list_price', string='Unit Price')
    subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)

    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price


class WorkOrder(models.Model):
    _name = 'work.order'
    _description = 'Work Order'

    name = fields.Char(string='Reference', default=lambda self: self.env['ir.sequence'].next_by_code('work.order'))
    car_repair_diagnosis_id = fields.Many2one('car.repair.diagnosis', string='Car Repair Diagnosis')
    work_order_id = fields.Char(string='Work Order')
    customer_name = fields.Char(string='Customer Name')
    service_details = fields.Text(string='Service Details')
    service_date = fields.Date(string='Date of Service')
    scheduled_date_planned = fields.Date(string='Scheduled Date Planned')
    end_date = fields.Date(string='End Date')
    num_of_hours = fields.Float(string='Total No. of Hours')
    hours_worked = fields.Float(string='Hours Worked')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('finished', 'Finished')
    ], string='Status', default='draft', readonly=True)

    def action_start_work(self):
        self.write({'state': 'in_progress'})

    def action_finish_work(self):
        self.write({'state': 'finished'})

    def action_work_order_print(self):
        return self.env.ref('car_repair_maintenance_axis.action_work_order_print').report_action(self)
