// Copyright (c) 2019, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Manual Attendance Correction', {
	refresh: function(frm) {
		frm.disable_save();
	},
	employee: function(frm){
		frappe.call({
			method: "frappe.client.get",
			args: {
				doctype: "Employee",
				"name":frm.doc.employee,
			},
			callback: function(r){
				if(r.message){
					frm.set_value("employee_name",r.message.employee_name);
				}
			}
		})
	},
	process: function(frm){
		if((frm.doc.employee) && (frm.doc.from_date) &&  (frm.doc.to_date)){
			frappe.call({
				method:"hunter_douglas.custom.bulk_att_adjust",
				args: {
					'employee': frm.doc.employee,
					'from_date':frm.doc.from_date,
					"to_date": frm.doc.to_date,
					"status": frm.doc.status
				},
				freeze:true,
				freeze_message:__('Processing...'),
				callback:function(r){
					show_alert(__("Attendance Updated"))
					setTimeout(function() { location.reload() }, 500);
				}
			})
		}
		if((frm.doc.location) && (frm.doc.from_date) &&  (frm.doc.to_date)){
			frappe.call({
				method:"hunter_douglas.custom.bulk_att_adjust",
				args: {
					'location': frm.doc.location,
					'from_date':frm.doc.from_date,
					"to_date": frm.doc.to_date,
					"status": frm.doc.status
				},
				freeze:true,
				freeze_message:__('Processing...'),
				callback:function(r){
					show_alert(__("Attendance Updated"))
					setTimeout(function() { location.reload() }, 500);
				}
			})
		}
	}
});
