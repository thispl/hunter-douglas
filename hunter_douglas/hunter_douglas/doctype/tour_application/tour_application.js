// Copyright (c) 2018, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Tour Application', {
	refresh: function(frm) {

	},
	validate: function(frm){
        frappe.call({
            "method": 'hunter_douglas.hunter_douglas.doctype.on_duty_application.on_duty_application.check_attendance',
            args: {
                "employee": frm.doc.employee,
                "from_date": frm.doc.from_date,
                "to_date": frm.doc.to_date
            },
            callback: function(r) {
                if (r.message) {
                    $.each(r.message, function(i, d) {
                        if(d.status == "Present"){
                            frappe.msgprint("Attendance already Marked as Present for "+d.attendance_date)
                            frappe.validated = false;
                        } else if(d.status == "Half Day"){
                            if(frm.doc.from_date == frm.doc.to_date){
                                if(frm.doc.from_date_session == "Full Day"){
                                    frappe.msgprint("Attendance already Marked as Half Day for "+d.attendance_date)
                                    frappe.validated = false;
                                } 
                            } else if(frm.doc.from_date != frm.doc.to_date){
                                if((frm.doc.from_date_session == "Full Day") || (frm.doc.to_date_session == "Full Day")){
                                    frappe.msgprint("Attendance already Marked as Half Day for "+d.attendance_date)
                                    frappe.validated = false;
                                }
                            
                        }
                    }
                    })
                }
            }
        });
    }
});
