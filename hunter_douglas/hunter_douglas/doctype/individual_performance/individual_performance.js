// Copyright (c) 2019, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Individual Performance', {
	onload: function (frm) {
	frm.get_field("sales_target").grid.only_sortable();   
        frm.get_field("management_pm_details").grid.only_sortable();           
        frm.set_query("employee_code", function () {
            return {
                "filters": {
                    "category": 'Management Staff',
                    "pms_on_hold": 0
                }
            }
        })
        cur_frm.fields_dict['sales_target'].grid.wrapper.find('.grid-add-row').hide();
        cur_frm.fields_dict['sales_target'].grid.wrapper.find('.grid-remove-rows').hide();
        cur_frm.fields_dict['management_pm_details'].grid.wrapper.find('.grid-add-row').hide();
        cur_frm.fields_dict['management_pm_details'].grid.wrapper.find('.grid-remove-rows').hide();
        cur_frm.fields_dict['competency_assessment1'].grid.wrapper.find('.grid-add-row').hide();
        cur_frm.fields_dict['competency_assessment1'].grid.wrapper.find('.grid-remove-rows').hide();

        frm.trigger("refresh")
        if(!frm.doc.small_text_12){
            frm.set_value("small_text_12", "-")
        }
        if(!frm.doc.small_text_14){
            frm.set_value("small_text_14", "-")
        }
        if(!frm.doc.small_text_16){
            frm.set_value("small_text_16", "-")
        }
        if(!frm.doc.small_text_18){
            frm.set_value("small_text_18", "-")
        }
        if(!frm.doc.required__job_knowledge){
            frm.set_value("required__job_knowledge", "-")
        }
        if(!frm.doc.training_required_to_enhance_job_knowledge){
            frm.set_value("training_required_to_enhance_job_knowledge", "-")
        }
        if(!frm.doc.required_skills){
            frm.set_value("required_skills", "-")
        }
        if(!frm.doc.training_required__to_enhance_skills_competencies){
            frm.set_value("training_required__to_enhance_skills_competencies", "-")
        }
        if(!frm.doc.potential_reviewer){
            frm.set_value("potential_reviewer", frm.doc.potential_hod)
        }
        if(!frm.doc.performance_reviewer){
            frm.set_value("performance_reviewer", frm.doc.performance_hod)
        }
        if(!frm.doc.promotion_reviewer){
            frm.set_value("promotion_reviewer", frm.doc.promotion_hod)
        }
        // if(!frm.doc.any_other_observations_reviewer){
        //     frm.set_value("any_other_observations_reviewer", frm.doc.any_other_observations_hod)
        // }
        // $.each(frm.doc.employee_feedback || [], function(i, v) {
		// 	if (!v.appraiser_remarks) {
		// 		frappe.model.set_value(v.doctype, v.name, "appraiser_remarks", v.hod)
		// 	}			
		// })
    },
    refresh: function (frm) {
        
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

        if(frm.doc.employee_code){
            frappe.call({
                "method": "frappe.client.get",
                args:{
                    "doctype": "Performance Management Calibration",
                    filters:{
                        "employee_code":frm.doc.employee_code,
                        "pm_year": frm.doc.pm_year
                    }
                },
                callback: function(r){
                    if(r.message.docstatus == 0){
                        frm.add_custom_button(__('Print'), function () {
                            // if (frm.doc.docstatus == "1"){
                        var me = this;
                    var doc = "Performance Management Calibration"
                    // frappe.call({
                    //     "method": "frappe.client.get",
                    //     args:{
                    //         "doctype": "Performance Management Calibration",
                    //         filters:{
                    //             "employee_code": frm.doc.employee_code,
                    //             "pm_year": frm.doc.pm_year
                    //         }
                    //     },
                    //     callback: function(r){
                            var f_name = r.message.name
                            var print_format = "Annexure";
                    var w = window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
                    +"doctype="+encodeURIComponent("Performance Management Calibration")
                    +"&name="+encodeURIComponent(f_name)
                    +"&trigger_print=1"
                    +"&format=" + print_format
                    +"&no_letterhead=0"
                    +(me.lang_code ? ("&_lang="+me.lang_code) : "")));
                        // }
                    // })
                })
                    }
                }
            })
        }
    }
});
