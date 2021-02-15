// Copyright (c) 2020, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Induction Test', {
	refresh: function (frm) {
		if (frappe.user.has_role("Employee")) {
			var df = frappe.meta.get_docfield("Test Questions", "score", cur_frm.doc.name);
			df.read_only = 1;
		}
		if (frappe.user.has_role("HOD")) {
			var df = frappe.meta.get_docfield("Test Questions", "question", cur_frm.doc.name);
			df.read_only = 1;
			var df = frappe.meta.get_docfield("Test Questions", "answers", cur_frm.doc.name);
			df.read_only = 1;
		}
		
	},
	validate(frm) {
		var total = 0
		$.each(frm.doc.questions, function (i, d) {
			total += Number(d.score)
		})
		frm.set_value("total_score", total)
		if (total > 50) {
			var today_date =frappe.datetime.nowdate()
			
			
			frappe.call({
				"method":"hunter_douglas.hunter_douglas.doctype.induction_test.induction_test.get_end_date",
				"args":{
				
				},
				callback: function(r){
					console.log(r)
					probation_end_date=r.message
					frappe.db.set_value('Employee', frm.doc.employee_id, {
						'employment_type': 'Probation',
						'probation_start_date': today_date,
						'probation_end_date' : r.message
					})
				}	
			})
		}
	},
    before_submit(frm){
		if (frm.doc.total_score < 50) {
			frappe.validated=false
			frappe.throw("Redo the induction")
		}
	},
});