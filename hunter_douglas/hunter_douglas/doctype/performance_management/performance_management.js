// Copyright (c) 2019, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on("Performance Management", {
	employee_code: function (frm) {
		frm.trigger("make_default_row")
		frappe.call({
			"method": "frappe.client.get_list",
			args: {
				"doctype": "Observation Feedback"
			},
			callback: function (r) {
				if (r.message) {
					$.each(r.message, function (i, d) {
						frappe.call({
							"method": "frappe.client.get",
							args: {
								doctype: "Observation Feedback",
								name: d.name
							},
							callback: function (r) {
								if (r.message) {
									var row = frappe.model.add_child(frm.doc, "PM Observation Feedback", "pm_observation_feedback");
									row.status = r.message.status;
								}
								refresh_field("pm_observation_feedback");
							}
						})
					})
				}
			}
		})
		frappe.call({
			"method": "frappe.client.get",
			args: {
				doctype: "Employee",
				filters: { "employee_number": frm.doc.employee_code }
			},
			callback: function (r) {
				if (r.message) {
					frm.set_value("employee_name", r.message.employee_name);
					frm.set_value("cost_code", r.message.cost_center);
					frm.set_value("designation", r.message.designation);
					frm.set_value("department", r.message.department);
					frm.set_value("date_of_joining", r.message.date_of_joining);
					frm.set_value("location", r.message.location_name);
					frm.set_value("year_of_last_promotion", r.message.year_of_last_promotion);
					frm.set_value("business_unit", r.message.business_unit);
					frm.set_value("grade", r.message.grade);

				}
			}
		})
		if (frm.doc.employee_code) {
			frappe.call({
				"method": "frappe.client.get_list",
				args: {
					doctype: "Competency"
				},
				callback: function (r) {
					if (r.message) {
						$.each(r.message, function (i, d) {
							frappe.call({
								"method": "frappe.client.get",
								args: {
									doctype: "Competency",
									name: d.name
								},
								callback: function (r) {
									if (r.message) {
										var row = frappe.model.add_child(frm.doc, "PM_Competency", "competency_assessment1");
										row.competency = r.message.competency;
										row.definition = r.message.definition;
										row.weightage = r.message.weightage;
									}
									refresh_field("competency_assessment1");
								}
							})
						})
					}
				}
			})

			frappe.call({
				"method": "frappe.client.get_list",
				args: {
					doctype: "Goal Settings",
					filters: { "employee": frm.doc.employee_code }
				},
				callback: function (r) {
					if (r.message) {
						$.each(r.message, function (i, d) {
							frappe.call({
								"method": "frappe.client.get",
								args: {
									doctype: "Goal Settings",
									name: d.name
								},
								callback: function (r) {
									if (r.message) {
										$.each(r.message.goals, function (i, d) {
											if (r.message.goals) {
												var row = frappe.model.add_child(frm.doc, "PM_Goal Setting", "key_result_area");
												row.goal_setting_for_current_year = d.goal_setting_for_current_year;
												row.performance_measure = d.performance_measure;
												row.weightage_w_100 = d.weightage_w_100;
												row.self_rating = d.self_rating;
												row.appraiser_rating_r = d.appraiser_rating_r;
												row.weighted_score = d.weighted_score;
											}
										})
										refresh_field("key_result_area")
									}
								}
							})
						})
					}
				}
			})
		}
	},
	validate: function (frm) {
		var child = frm.doc.competency_assessment1;
		var len = child.length;
		var total = 0.0;
		var ava = 0.0;
		for (var i = 0; i < len; i++) {
			total += child[i].total;
		}
		ava = ((total / len) * 10).toFixed(1)
		frm.set_value("average_score_attained", ava);
	},
	onload: function(frm){
		d= new Date()
		var pastYear = d.getFullYear() - 1;
		d.setFullYear(pastYear);
		$('h6:contains("Goal Setting - Last Year")').text('Goal Setting - '+(new Date().getFullYear()));
		$('h6:contains("Goal Setting - Current Year")').text('Goal Setting - '+pastYear);
		frm.trigger("refresh")
		frm.trigger("make_default_row")
	},
	refresh: function (frm) {
		if (frappe.user.has_role("One Above Manager")) {
            var df = frappe.meta.get_docfield("PM_Competency", "hod", cur_frm.doc.name);
			df.read_only = 1;
			var df1 = frappe.meta.get_docfield("PM_Competency", "reviewer", cur_frm.doc.name);
            df1.read_only = 1;
		}
		if (frappe.user.has_role("HOD")) {
            var df = frappe.meta.get_docfield("PM_Competency", "appraiser_rating", cur_frm.doc.name);
			df.read_only = 1;
			var df1 = frappe.meta.get_docfield("PM_Competency", "reviewer", cur_frm.doc.name);
            df1.read_only = 1;
		}
		if (frappe.user.has_role("Employee")) {
            var df = frappe.meta.get_docfield("PM_Competency", "appraiser_rating", cur_frm.doc.name);
			df.read_only = 1;
			var df1 = frappe.meta.get_docfield("PM_Competency", "reviewer", cur_frm.doc.name);
			df1.read_only = 1;
			var df = frappe.meta.get_docfield("PM_Competency", "hod", cur_frm.doc.name);
			df.read_only = 1;
        }
		frm.trigger("make_default_row")
		// var df = frappe.meta.get_docfield("Job Analysis","appraisee_remarks",frm.doc.name);
		// df.in_list_view = 1;
		// // frm.fields_dict["job_analysis"].grid.set_df_property("appraisee_remarks", "in_list_view", 1);
		// // job_analysis_grid.set_editable_grid_column_disp("appraisee_remarks", true);
		// return df
		// var n = 3;
		// for (var i = 0; i < n; i++) {
		// 	var row = frappe.model.add_child(frm.doc, "Job Analysis", "job_analysis");
		// 	row.appraisee_remarks = "";
		// }
		// refresh_field("job_analysis");
		// var df = frappe.meta.get_docfield("Job Analysis","appraisee_remarks", cur_frm.doc.name);
		// df.in_list_view = 1;
		var grid =  cur_frm.fields_dict["job_analysis"].grid;
		grid.fields_dict.appraisee_remarks.$wrapper.show();
		// cur_frm.fields_dict.job_analysis.grid.fields_map. appraisee_remarks.in_list_view = 1;
		cur_frm.refresh_field("job_analysis");

	},
	make_default_row: function(frm){
		if(frm.doc.employee_code){
			for(var i=0;i<5;i++){
				var row = frappe.model.add_child(frm.doc, "Job Analysis","job_analysis");
				row.appraisee_remarks == ""
			}
			refresh_field("job_analysis")
			for(var i=0;i<5;i++){
				var row = frappe.model.add_child(frm.doc, "Goal Settings 1","key_results_area");
				row.appraisee_remarks == ""
			}
			refresh_field("key_results_area")
			for(var i=0;i<5;i++){
				var row = frappe.model.add_child(frm.doc, "PM_Goal Setting","key_result_area");
				row.appraisee_remarks == ""
			}
			refresh_field("key_result_area")
			for(var i=0;i<5;i++){
				var row = frappe.model.add_child(frm.doc, "Employee Feedback","employee_feedback1");
				row.appraisee_remarks == ""
			}
			refresh_field("employee_feedback1")
		}
	}
})
frappe.ui.form.on("PM_Competency", {
	reviewer: function (frm, cdt, cdn) {
		var child = locals[cdt][cdn];
		if (child.appraiser_rating) {
			var total = (child.reviewer * (10 / 100))
			frappe.model.set_value(child.doctype, child.name, "total", total);
		}
	},
	hod: function(frm,cdt,cdn){
		var child = locals[cdt][cdn]	
        if (child.hod <= child.weightage_w_100) {
            frappe.model.set_value(cdt, cdn, "reviewer", child.hod)

        } 
	}
})
frappe.ui.form.on("Goal Setting", {
	reviewer: function (frm, cdt, cdn) {
		var child = locals[cdt][cdn];
		if (child.appraiser_rating_r) {
			var total = (child.reviewer * (child.weightage_w_100 / 100))
			frappe.model.set_value(child.doctype, child.name, "weighted_score", total);
		}
	},
	hod: function(frm,cdt,cdn){
		var child = locals[cdt][cdn]	
        if (child.hod <= child.weightage_w_100) {
            frappe.model.set_value(cdt, cdn, "reviewer", child.hod)

        } 
	}
})
frappe.ui.form.on("Goal Settings 1", {
	reviewer: function (frm, cdt, cdn) {
		var child = locals[cdt][cdn];
		if (child.appraiser_rating_r) {
			var total = (child.reviewer * (child.weightage_w_100 / 100))
			frappe.model.set_value(child.doctype, child.name, "weighted_score", total);
		}
	},
	hod: function(frm,cdt,cdn){
		var child = locals[cdt][cdn]	
        if (child.hod <= child.weightage_w_100) {
            frappe.model.set_value(cdt, cdn, "reviewer", child.hod)

        } 
	}
})

