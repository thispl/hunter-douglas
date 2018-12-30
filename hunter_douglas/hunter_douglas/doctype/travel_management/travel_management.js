// Copyright (c) 2018, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Travel Management', {
	refresh: function(frm) {
        if (frm.doc.docstatus == 1 && frm.doc.status == 'Approved')
        {
		// frm.add_custom_button(__("Expense Claim"),function(){
		// 	if (frm.doc.expense_claim){

		// 		frappe.set_route("Form","Expense Claim",frm.doc.expense_claim)
		// 	}
		// 	else{
		// 		frappe.route_options = {
		// 			"travel_management": frm.doc.name,
		// 		},
		// 		frappe.set_route("Form","Expense Claim","New Expense Claim 1")
		// 	}
			
		// })
    }
    },  
	from_date: function(frm) {
        frm.trigger("calculate_total_days");
    },
    to_date: function(frm) {
        frm.trigger("calculate_total_days");
    },
    to_date_session: function(frm){
        frm.trigger("calculate_total_days")
    },
    from_date_session: function(frm){
        frm.trigger("calculate_total_days")
        if(frm.doc.from_date == frm.doc.to_date){
            frm.set_value("to_date_session", frm.doc.from_date_session)
        }
    },
    calculate_total_days: function(frm) {
        if(frm.doc.from_date && frm.doc.to_date && frm.doc.employee) {
            var date_dif = frappe.datetime.get_diff(frm.doc.to_date, frm.doc.from_date) + 1
            return frappe.call({
                "method": 'hunter_douglas.hunter_douglas.doctype.travel_management.travel_management.get_number_of_leave_days',
                args: {
                    "employee": frm.doc.employee,
                    "from_date": frm.doc.from_date,
                    "from_date_session":frm.doc.from_date_session,
                    "to_date": frm.doc.to_date,
                    "to_date_session":frm.doc.to_date_session,
                    "date_dif": date_dif
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value('total_number_of_days', r.message);
                        frm.trigger("get_leave_balance");
                    }
                }
            });
        }
    }
});
