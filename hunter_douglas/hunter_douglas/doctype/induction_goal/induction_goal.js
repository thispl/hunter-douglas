// Copyright (c) 2020, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Induction Goal', {
	refresh: function(frm) {
		frm.toggle_display("hod",false)
		frm.toggle_display("hr_manager",false)
		frm.toggle_display("reviewer",false)
		if (frappe.user.has_role("HR Manager")) {
			frm.toggle_display("hr_manager",true)
		}
		if (frappe.user.has_role("HOD")) {
			frm.toggle_display("hod",true)
		}
		if (frappe.user.has_role("Reviewer")) {
			frm.toggle_display("reviewer",true)
		}	
	},
	before_submit(frm) {
		if (frappe.user.has_role("Reviewer")) {
			if(frm.doc.reviewer=="Confirmed"){
				console.log(frm.doc.employee_id)
				frappe.db.set_value("Employee", frm.doc.employee_id, "status", "Active")
				console.log(frm.doc.employee_id)
			}
		}
		
	}
});
