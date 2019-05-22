// Copyright (c) 2018, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Job Applicant', {
	refresh: function(frm) {
		frappe.call({
			"method": "frappe.client.get_list",
			args: {
				doctype: "Evaluation Keys"
			},
			callback: function (r) {
				if (r.message) {
					$.each(r.message, function (i, d) {
						frappe.call({
							"method": "frappe.client.get",
							args: {
								doctype: "Evaluation Keys",
								name: d.name
							},
							callback: function (r) {
								if (r.message) {
									// console.log(r.message.name)
									var row = frappe.model.add_child(frm.doc,  "Interview Evaluation Keys", "interview_evaluation_keys");
									row.label = d.name
									row.weightage_w = r.message.weightage;
								}
								
								
								refresh_field("interview_evaluation_keys");
								
								
							}
						})
		
					})
				}
			}
		})
		

	}
});


// frappe.call({
// 	"method": "frappe.client.get_list",
// 	args: {
// 		doctype: "Evaluation Keys"
// 	},
// 	callback: function (r) {
// 		if (r.message) {
// 			$.each(r.message, function (i, d) {
// 				frappe.call({
// 					"method": "frappe.client.get",
// 					args: {
// 						doctype: "Evaluation Keys",
// 						name: d.name
// 					},
// 					callback: function (r) {
// 						if (r.message) {
							
// 							var row = frappe.model.add_child(frm.doc,  "Interview Evaluation Keys", "interview_evaluation_keys");
// 							row.weightage = r.message.weightage;
// 						}
						
						
// 						refresh_field("interview_evaluation_keys");
						
						
// 					}
// 				})

// 			})
// 		}
// 	}
// })
