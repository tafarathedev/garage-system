from odoo import models, fields


class Car(models.Model):
    _name = 'car'
    _description = 'Car Management'

    owner_id = fields.Many2one('res.partner', string='Owner', required=True)
    name = fields.Char(string='Car Name', required=True)
    car_num = fields.Char(string='Car Number')
    brand = fields.Char(string='Brand', required=True)
    model = fields.Char(string='Model', required=True)
    manufacturing_year = fields.Integer(string='Manufacturing Year')
    fuel_type = fields.Selection([
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('hybrid', 'Hybrid'),
        ('electric', 'Electric')], string='Fuel Type')
    color = fields.Char(string='Color')
    car_notes = fields.Text(string='Car Notes')


class CarParts(models.Model):
    _name = 'car.parts'
    _description = 'Car Parts'

    product_id = fields.Many2one('product.product', string='Product')
    product_variant_id = fields.Many2one('product.product', string='Product Variant')
    part_name = fields.Char(string='Parts Name', required=True)
    description = fields.Text(string='Description')

    def name_get(self):
        result = []
        for record in self:
            name = record.part_name or ""
            result.append((record.id, name))
        return result


class CarProject(models.Model):
    _name = 'car.project'
    _description = 'Car Project'

    name = fields.Char(string='Project Name', required=True)
    car_id = fields.Many2one('car', string='Car')
    task_ids = fields.One2many('car.project.task', 'project_id', string='Tasks')


class CarProjectTask(models.Model):
    _name = 'car.project.task'
    _description = 'Car Project Task'

    name = fields.Char(string='Task Name', required=True)
    project_id = fields.Many2one('car.project', string='Project', ondelete='cascade')
    car_id = fields.Many2one('car', string='Car')
    user_id = fields.Many2one('res.users', string='Assigned To')
    planned_hours = fields.Float(string='Planned Hours')
    timesheet_ids = fields.One2many('car.project.task.timesheet', 'task_id', string='Timesheets')


class CarProjectTaskTimesheet(models.Model):
    _name = 'car.project.task.timesheet'
    _description = 'Car Project Task Timesheet'

    task_id = fields.Many2one('car.project.task', string='Task')
    user_id = fields.Many2one('res.users', string='User', required=True, default=lambda self: self.env.user)
    date = fields.Date(string='Date', required=True, default=fields.Date.context_today)
    duration = fields.Float(string='Duration', required=True)
    description = fields.Text(string='Description')
    # car_repair_id = fields.Many2one('car.repair.form', string='Car Repair')

