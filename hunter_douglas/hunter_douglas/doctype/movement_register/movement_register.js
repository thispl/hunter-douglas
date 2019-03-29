// Copyright (c) 2018, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Movement Register', {
	refresh:function(frm){
		var from_time_picker = frm.fields_dict.from_time.datepicker;
		var pre = frappe.datetime.add_days(frappe.datetime.now_date(), -1);
		var nxt = frappe.datetime.add_days(frappe.datetime.now_date(), 1);
		from_time_picker.update({
			showSecond: false,
			maxSeconds: 00,
			minDate: frappe.datetime.str_to_obj(pre),
			maxDate: frappe.datetime.str_to_obj(nxt)
		})
		var to_time_picker = frm.fields_dict.to_time.datepicker;
		to_time_picker.update({
			showSecond: false,
			maxSeconds: 00,
			minDate: frappe.datetime.str_to_obj(pre),
			maxDate: frappe.datetime.str_to_obj(nxt)
		})
		if(frm.doc.is_from_ar){
            frm.add_custom_button(__('Back'), function () {
                frappe.set_route("query-report", "Attendance recapitulation")
            });
        }
	},
	validate: function(frm){
		if(frm.doc.is_from_ar == "Yes"){
            frappe.set_route("query-report", "Attendance recapitulation")
        }
	}
});
