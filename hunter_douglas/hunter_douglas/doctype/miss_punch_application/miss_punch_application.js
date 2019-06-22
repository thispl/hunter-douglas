// Copyright (c) 2019, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Miss Punch Application', {
	refresh: function(frm) {

	},
	validate: function(frm){
		if((frm.doc.attendance_date >= frappe.datetime.nowdate()) && frm.doc.attendance_date){
			validated = false
			frm.set_value("attendance_date","")
			frappe.throw("Attendance Can't be marked for Future Date")			
		}
		if(frm.doc.attendance_date < frappe.datetime.nowdate()){
			frappe.call({
				"method": "hunter_douglas.hunter_douglas.doctype.miss_punch_application.miss_punch_application.check_attendance",
				args:{
					"attendance_date":frm.doc.attendance_date,
					"employee": frm.doc.employee
				},
				callback: function(r){
					if(r.message != "OK"){
						if(r.message.in_time && r.message.out_time){
							validated = false;
							frappe.msgprint("Attendance Already Marked")
						} else {
							frm.set_value("status","Applied")
							frappe.msgprint("Miss Punch Applied Successfully")

						}
					} 
					if(frm.doc.reason.length <= 100){
						frappe.validated = false;
						frappe.msgprint("Reason must contain 100 charaters")
					} else {
						frm.set_value("status","Applied")
						frappe.msgprint("Miss Punch Applied Successfully")
					}
				}
			})
		}
		
	},
	employee: function(frm){
		frappe.call({
			method: 'frappe.client.get',
			args: {
				doctype: 'Employee',
				name: frm.doc.employee
			},
			callback: function (r) {
				var LA = r.message.leave_approvers
				frm.set_value("approver", LA[0].leave_approver)
				frm.set_value("employee_name",r.message.employee_name)
			}
		})
	},
	before_submit:function(frm){
		if(frappe.session.user != frm.doc.approver){
			frappe.validated = false;
			frappe.msgprint(__("The Selected Approver only can submit this Document"));
		}
	}, 
	onload: function(frm){
		if(frappe.session.user == frm.doc.approver){
			frm.set_df_property('status', 'read_only', 0);
		}
	},
});
