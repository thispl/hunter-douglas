import frappe

@frappe.whitelist(allow_guest=True)
def mark_checkin(**args):
    if not frappe.db.exists('Employee Checkin',{'employee':args['employee'],'time':args['time']}):
        if frappe.db.exists('Employee',{'name':args['employee']}):
            ec = frappe.new_doc('Employee Checkin')
            ec.employee = args['employee'].upper()
            ec.time = args['time']
            ec.device_id = args['device_id']
            ec.log_type = 'IN'
            ec.save(ignore_permissions=True)
            frappe.db.commit()
            return "Checkin Marked"
    else:
        return "Checkin Marked"