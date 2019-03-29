// Copyright (c) 2019, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Performance Management Manager', {
	refresh: function(frm) {

	},
	onload: function(frm){
		var child1 = frm.doc.pm_observation_feedback;
        var len1 = child1.length;
        if (!len1) {
		// frappe.call({
		// 	"method": "frappe.client.get_list",
		// 	args: {
		// 		"doctype": "Observation Feedback"
		// 	},
		// 	callback: function (r) {
		// 		if (r.message) {
		// 			$.each(r.message, function (i, d) {
		// 				frappe.call({
		// 					"method": "frappe.client.get",
		// 					args: {
		// 						doctype: "Observation Feedback",
		// 						name: d.name
		// 					},
		// 					callback: function (r) {
		// 						if (r.message) {
		// 							var row = frappe.model.add_child(frm.doc, "PM Observation Feedback", "pm_observation_feedback");
		// 							row.status = r.message.status;
		// 						}
		// 						refresh_field("pm_observation_feedback");
		// 					}
		// 				})
		// 			})
		// 		}
		// 	}
		// })
		for( var i = 0 ;i <4 ; i++){
			var row = frappe.model.add_child(frm.doc, "PM Observation Feedback", "pm_observation_feedback");
			if(i = 0){
				row.status = "Potential (High/Medium/Low)";
			}
			if(i = 1){
				row.status = "Performance (Excellent/Meets Expectation/Average/Under Performance";
			}
			if(i = 2){
				row.status = "Promoted to next grade/ May be considered after 1or 2 years/Not yet ready ";
			}
			if(i = 3){
				row.status = "Any other observations ";
			}
		}
		refresh_field("pm_observation_feedback");
	}
	d = new Date()
        frm.set_value("appraisal_year", String(d.getFullYear() - 1))
        if (frm.doc.__islocal) {
            for (var i = 2016; i < d.getFullYear(); i++) {
                var row = frappe.model.add_child(frm.doc, "PM Sales Target", "sales_target");
                row.year = i.toString()
            }
            refresh_field("sales_target")

        }

        var pastYear = d.getFullYear() - 1;
        d.setFullYear(pastYear);
        $('h6:contains("Goal Setting - Last Year")').text('Goal Setting - ' + (new Date().getFullYear()));
        $('h6:contains("Goal Setting - Current Year")').text('Goal Setting - ' + pastYear);
		cur_frm.fields_dict['sales_target'].grid.wrapper.find('.grid-add-row').hide();
        cur_frm.fields_dict['sales_target'].grid.wrapper.find('.grid-remove-rows').hide();
        cur_frm.fields_dict['competency_assessment1'].grid.wrapper.find('.grid-add-row').hide();
        cur_frm.fields_dict['competency_assessment1'].grid.wrapper.find('.grid-remove-rows').hide();
        frm.trigger("refresh")
		var child = frm.doc.employee_feedback;
        var len = child.length;
        if (!len) {
		if(frm.doc.employee_code){
			for (var i = 0; i < 5; i++) {
				var row = frappe.model.add_child(frm.doc, "Employee Feedback", "employee_feedback");
				row.appraisee_remarks == ""
			}
			refresh_field("employee_feedback")
		}
	}
	},
	on_submit: function (frm) {
        var child1 = frm.doc.key_result_area;
        var len1 = child1.length;
        var total1 = 0.0;
        if (len1) {
            for (var i = 0; i < len1; i++) {
                total1 += child1[i].weightage;
            }
            if(total1 != 100){
                validated = false
                frappe.throw(__("In Goal Setting Weightage Must be equal to 100"))
            }
        }
        var child = frm.doc.key_results_area;
        var len = child.length;
        var total = 0.0;
        if (len) {
            for (var i = 0; i < len; i++) {
                total += child[i].weightage;
            }
            if(total != 100){
                validated = false
                frappe.throw(__("In Previous Goal Setting Weightage Must be equal to 100"))
            }
        }
    },
});

frappe.ui.form.on("PM Competency Manager", {
    before_competency_assessment1_remove: function (frm, cdt, cdn) {
        frappe.throw(__("Item cannot be deleted"))
	}
})
