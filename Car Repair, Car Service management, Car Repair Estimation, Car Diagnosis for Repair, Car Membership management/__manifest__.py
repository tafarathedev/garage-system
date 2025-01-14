{
    'name': "Car Repair, Car Service management, Car Repair Estimation, Car Diagnosis for Repair, Car Membership management",
    'description' : "Car Repair and Maintenance module for records of Car Repairing and Service",
    'summary':'Car Repair, Car Service management, Car Repair Estimation, Car Diagnosis for Repair, Car Maintenance, vehicle repair, Car Membership management,workshop automobile repair service repair Automotive repair website car repair',
	'depends': ['base','sale_management','hr_maintenance','stock','project','account','hr_timesheet', 'website','mail'],
    'version': '16.0.8',
	'data': [
	'security/ir.model.access.csv',
	'security/record_rules.xml',
	'view/cars.xml',
	'view/car_parts.xml',
	'view/car_repair_dashboard.xml',
	'view/car_repair_membership.xml',
	'view/membership_plan.xml',
	'view/service_repair_options.xml',
	'view/user_roles.xml',
	'view/car_service.xml',
	'view/car_service_type.xml',
	'view/car_repair_form.xml',
	'view/car_repair_estimate.xml',
	'view/car_repair_team.xml',
        'view/maintenance_checklist.xml',
        'view/car_diagnosis.xml',
        'data/car_repair_portal.xml',
        'view/car_portal.xml',
        'view/car_website_portal.xml',
        'view/work_order_view.xml',
        'view/car_repair_request.xml',
        'reports/car_repair_receipt_report.xml',
        'reports/car_repair_label_report.xml',
        'reports/car_repair_checklists.xml',
        'reports/car_diagnosis_request.xml',
        'reports/car_diagnosis_result.xml',
        'reports/work_order_report.xml',
        'reports/car_repair_estimate.xml',
    ],   

    'installable': True,
    'assets': {
        'web.assets_backend': [
            'car_repair_maintenance_axis/static/src/xml/car_repair_dashboard.xml',
            '/car_repair_maintenance_axis/static/src/js/car_repair_dashboard.js',
            '/car_repair_maintenance_axis/static/src/js/jquery.dataTables.min.js',
            '/car_repair_maintenance_axis/static/src/js/datatables.min.js',
            '/car_repair_maintenance_axis/static/src/js/dataTables.buttons.min.js',
            '/car_repair_maintenance_axis/static/src/js/Chart.js',
            '/car_repair_maintenance_axis/static/src/css/nv.d3.css',
            'https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css',
            'car_repair_maintenance_axis/static/src/scss/new_css.css',
        ],
    },
    'auto_install': False,
   'license': 'OPL-1',
    'price': 130,
    'currency': 'USD',
    'support': 'business@axistechnolabs.com',
    'author': 'Axis Technolabs',
    'website': 'https://www.axistechnolabs.com',
    'images': ['static/description/car_repair_banner.png'],
}
