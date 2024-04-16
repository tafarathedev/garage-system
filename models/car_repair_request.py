import calendar as cal

from odoo import fields, models, api, _


class CarRepair(models.Model):
    _name = 'car.repair.request'
    _description = 'Car Repair Request Form'

    name = fields.Char(string='Name')
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    reason_for_repair = fields.Char(string='Reason For Repair')
    service = fields.Char(string='Service')

    service_id = fields.Many2one('car.service', string='Car Service')
 
    # car_id = fields.Many2one('car', string='Car', required=True, create=True)
    car_id = fields.Many2one('car', string='Car')
    brand = fields.Char(related='car_id.brand', string='Brand', readonly=True)

    car_brand = fields.Char(string='Car Brand')
    priority = fields.Selection([("0", ("Low")), ("1", ("Medium")), ("2", ("High")), ("3", ("Very High"))],
                                string="Priority", default="1")
    reason_details = fields.Text("Reason For Repair In Details")
    list_of_damage = fields.Char("List Of Damage")

    # attachment_ids = fields.Many2many('ir.attachment', 'attachment_id', 'car_repair_res_id',
    #                                   string="Attachment",
    #                                   help='You can attach the copy of your document', copy=False)
    attachment = fields.Binary(string='attachment', attachment=True)
    car_repair_id = fields.Many2one('car.repair.form', string='Car Repair', readonly=True, copy=False)
    approved = fields.Boolean(string='Approved', default=False)
    customer_id = fields.Many2one('res.partner', string='Customer Name')

    def action_approve_request(self):
        for record in self:
            partner_Obj =self.env['res.partner']
            partner = partner_Obj.search([('name','=',record.name),('email','=',record.email)],limit=1)
            if not partner:
                partner = partner_Obj.create({'name':record.name,'email':record.email})
            if not self.env['car.repair.form'].search([('car_repair_request_id','=',record.id)]):
                car_repair_vals = {
                    'name': record.name,
                    'customer': partner.id,
                    'car_id': record.car_id.id,
                    'car_repair_request_id': record.id
                    # Add other required fields
                }
                create_form_id = self.env['car.repair.form'].create(car_repair_vals)
                record.car_repair_id = create_form_id.id
                record.approved = True
