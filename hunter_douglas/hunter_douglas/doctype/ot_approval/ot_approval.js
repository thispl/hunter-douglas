// Copyright (c) 2021, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('OT Approval', {
	// refresh: function(frm) {

	// }
});
frappe.ui.form.on('OT Table',"submit",function(frm,cdt,cdn) {
	var child =locals[cdt][cdn]
	frm.call('update_attendance',{
		row:child,
	}).then(r =>{
		
	})

});

