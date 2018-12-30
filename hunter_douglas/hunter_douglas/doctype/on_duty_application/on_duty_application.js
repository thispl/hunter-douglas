// Copyright (c) 2018, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('On Duty Application', {
    refresh: function(frm) {

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
                "method": 'hunter_douglas.hunter_douglas.doctype.on_duty_application.on_duty_application.get_number_of_leave_days',
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
