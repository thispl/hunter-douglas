// Copyright (c) 2020, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Manpower Requisition Request', {
	refresh: function(frm) {

	},
	onload:function(frm){
		frm.set_value("name_of_intender",frappe.session.user)
	}

});
