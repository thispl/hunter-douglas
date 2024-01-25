// Copyright (c) 2022, teampro and contributors
// For license information, please see license.txt

frappe.ui.form.on('Attendance Regularization', {
	
	attendance_date(frm){
		// frappe.call({
		// 	method:'infac.infac.doctype.attendance_regularize.attendance_regularize.get_assigned_shift_details',
		// 	args:{
		// 		emp:frm.doc.employee,
		// 		att_date:frm.doc.attendance_date
		// 	},
		// 	callback(r){
		// 		$.each(r.message,function(i,v){
		// 			frm.set_value('assigned_shift',v.shift_assign)
		// 			frm.set_value('shift_in_time',v.shift_start_time)
		// 			frm.set_value('shift_out_time',v.shift_end_time)
		// 		})
		// 	}
		// })
		frappe.call({
			method:'hunter_douglas.hunter_douglas.doctype.attendance_regularization.attendance_regularization.get_attendance',
			args:{
				emp:frm.doc.employee,
				att_date:frm.doc.attendance_date
			},
			callback(r){
				$.each(r.message,function(i,v){
					frm.set_value('first_in_time',v.in_time)
					frm.set_value('last_out_time',v.out_time)
					
				})
			}
		})
		frappe.call({
			method:'hunter_douglas.hunter_douglas.doctype.attendance_regularization.attendance_regularization.attendance_marked',
			args:{
				emp:frm.doc.employee,
				att_date:frm.doc.attendance_date,
			},
			callback(r){
				$.each(r.message,function(i,v){
					console.log(v.status_)
					frm.set_value('corrected_in_time',v.in_time)
					frm.set_value('corrected_out_time',v.out_time)
					frm.set_value('corrected_status',v.status_)
					frm.set_value('attendance_marked',v.att_id)
					frm.set_value('total_working_hours',v.total_working_hours)
					frm.set_value('overtime_hours',v.overtime_hours)
					frm.set_value('status',v.status_)
				})

			}
		})
	}
});
