// Copyright (c) 2019, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Performance Management HOD', {
	refresh: function(frm) {

	},
	onload: function(frm){
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

        // frm.trigger("refresh")
	}
});

frappe.ui.form.on("PM Competency HOD", {
    before_competency_assessment1_remove: function (frm, cdt, cdn) {
        frappe.throw(__("Item cannot be deleted"))
	}
})
