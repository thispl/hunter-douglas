// Copyright (c) 2018, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Travel Management', {
	refresh: function(frm) {
		frm.add_custom_button(__("Expense Claim"),function(){
			if (frm.doc.expense_claim){

				frappe.set_route("Form","Expense Claim",frm.doc.expense_claim)
			}
			else{
				frappe.route_options = {
					"travel_management": frm.doc.name,
				};
				frappe.set_route("Form","Expense Claim","New Expense Claim 1")
			}
			
		})

	},
});
