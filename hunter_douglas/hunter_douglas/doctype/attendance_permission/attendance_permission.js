// Copyright (c) 2019, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Attendance Permission', {
	refresh: function (frm) {

	},
	to_time: function (frm) {
		var diff = frm.doc.to_time - frm.doc.from_time
		console.log(diff)
		var from_time = new Date(frm.doc.from_time)
		var to_time = new Date(frm.doc.to_time)
		var time_diff = (to_time - from_time)
		var hours = ((time_diff) / 3600000)
		frm.set_value("total_permission_hour", hours)
			},
	employee:function(frm){
		frappe.call({
			method:"hunter_douglas.custom.att_permission",
			args:{
				"employee":frm.doc.employee
			},
			callback:function(r){
				
			}
		})

		
	}
});
