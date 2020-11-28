// Copyright (c) 2018, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('On Duty Application', {
    refresh: function (frm) {
        if (frm.doc.is_from_ar) {
            frm.add_custom_button(__('Back'), function () {
                frappe.set_route("query-report", "Attendance recapitulation")
            });
        }
    },
    from_date: function (frm) {
        frm.trigger('validate_cutoff')
        frm.trigger("calculate_total_days")
        if (frm.doc.to_date && frm.doc.from_date) {
            if (frm.doc.from_date != frm.doc.to_date) {
                if (frm.doc.from_date < frm.doc.to_date) {
                    frm.trigger("calculate_total_days")
                } else {
                    validated = false
                    frappe.msgprint("From Date Must be Lesser than or Equal to To Date")
                    frm.set_value("from_date", "")
                }
            }
        }


    },
    to_date: function (frm) {
        frm.trigger("calculate_total_days")
        if (frm.doc.from_date && frm.doc.to_date) {
            if (frm.doc.from_date != frm.doc.to_date) {
                if (frm.doc.from_date < frm.doc.to_date) {
                    frm.trigger("calculate_total_days")
                } else {
                    validated = false
                    frappe.msgprint("To Date Must be Greater than or Equal to From Date")
                    frm.set_value("to_date", "")
                }
            }
        }
    },
    to_date_session: function (frm) {
        if (frm.doc.from_date == frm.doc.to_date) {
            frm.set_value("from_date_session", frm.doc.to_date_session)
        }
        frm.trigger("calculate_total_days")
    },
    from_date_session: function (frm) {
        frm.trigger("calculate_total_days")
        if (frm.doc.from_date == frm.doc.to_date) {
            frm.set_value("to_date_session", frm.doc.from_date_session)
        }
    },
    calculate_total_days: function (frm) {
        if (frm.doc.from_date && frm.doc.to_date && frm.doc.employee) {
            var date_dif = frappe.datetime.get_diff(frm.doc.to_date, frm.doc.from_date) + 1
            return frappe.call({
                "method": 'hunter_douglas.hunter_douglas.doctype.on_duty_application.on_duty_application.get_number_of_leave_days',
                args: {
                    "employee": frm.doc.employee,
                    "from_date": frm.doc.from_date,
                    "from_date_session": frm.doc.from_date_session,
                    "to_date": frm.doc.to_date,
                    "to_date_session": frm.doc.to_date_session,
                    "date_dif": date_dif
                },
                callback: function (r) {
                    if (r.message) {
                        frm.set_value('total_number_of_days', r.message);
                        frm.trigger("get_leave_balance");
                    }
                }
            });
        }
    },
    validate: function (frm) {
        // if(frm.doc.employee){
        //     frappe.call({
        //         "method": 'hunter_douglas.update_attendance.check_other_docs',
        //         args: {
        //             "employee": frm.doc.employee,
        //             "from_date": frm.doc.from_date,
        //             "to_date": frm.doc.to_date,
        //             "from_date_session": frm.doc.from_date_session,
        //             "to_date_session": frm.doc.to_date_session
        //         },
        //         callback: function (r) {
        //             if(r.message != 0){
        //                 var type = r.message.type 
        //                 var date = r.message.date
        //                 validated = false
        //                 var s = "You Already Applied type on date"
        //                 var rs = s.replace("type",type).replace("date",date)
        //                 frappe.msgprint(rs)
        //             }
        //         }
        //     })
        // }      
        // if(frappe.user.has_role("Auto Present Employee")){
        //     list = ["singh.ak@hunterdouglas.in","sundar@hunterdouglas.in","venkatesh.v@hunterdouglas.in","raghavan.s@hunterdouglas.in","joshy@hunterdouglas.in","udaya.kumar@hunterdouglas.in","ananya.das@hunterdouglas.in","ayushi.roy@hunterdouglas.in","edwin.raj@turnils-mermet.asia",
        //     "sanjay.pm@turnils-mermet.asia","ramakrishnan.p@hunterdouglas.in"]
        //     status = ""
        //     for(var i=0; i<11; i++){
        //         if(status == ""){
        //             if(frappe.session.user == list[i]){
        //             status = "Yes" 
        //             }
        //         }
        //     }
        //     if(status == "Yes"){
        //         frappe.call({
        //             "method": 'hunter_douglas.custom.check_attendance_status',
        //             args: {
        //                 "employee": frm.doc.employee,
        //                 "from_date": frm.doc.from_date,
        //                 "to_date": frm.doc.to_date
        //             },
        //             callback: function (r) {
        //                 frappe.msgprint("OD Applied Successfully")
        //             }
        //         })
        //     }
        // }
        frm.trigger('validate_cutoff')
        if (!frappe.user.has_role("Auto Present Employee") && (frappe.user.has_role("Employee")) && frm.doc.from_date && frm.doc.employee && frm.doc.to_date) {
            frappe.call({
                "method": 'hunter_douglas.hunter_douglas.doctype.on_duty_application.on_duty_application.check_attendance',
                args: {
                    "employee": frm.doc.employee,
                    "from_date": frm.doc.from_date,
                    "to_date": frm.doc.to_date
                },
                callback: function (r) {
                    if (r.message) {
                        $.each(r.message, function (i, d) {
                            if (d.status == "Present") {
                                frappe.msgprint("Attendance already Marked as Present for " + d.attendance_date)
                                frappe.validated = false;
                            } else if (d.status == "Half Day") {
                                if (frm.doc.from_date == frm.doc.to_date) {
                                    if (frm.doc.from_date_session == "Full Day") {
                                        frappe.msgprint("Attendance already Marked as Half Day for " + d.attendance_date)
                                        frappe.validated = false;
                                    }
                                } else if (frm.doc.from_date != frm.doc.to_date) {
                                    if ((frm.doc.from_date_session == "Full Day") || (frm.doc.to_date_session == "Full Day")) {
                                        frappe.msgprint("Attendance already Marked as Half Day for " + d.attendance_date)
                                        frappe.validated = false;
                                    }

                                }
                            }
                        })
                    }
                }
            });
        }
        if (frm.doc.is_from_ar && frm.doc.status == "Applied") {
            frappe.set_route("query-report", "Attendance recapitulation")
        }
    },
    validate_cutoff: function (frm) {
        if (frappe.session.user == 'sivaranjani.s@hunterdouglas.in') {
            frappe.call({
                "method": 'hunter_douglas.hunter_douglas.doctype.on_duty_application.on_duty_application.validate_cutoff',
                args: {
                    "from_date": frm.doc.from_date
                },
                callback: function (r) {
                    if (r.message == 'Expired') {
                        frappe.validated = false;
                        refresh_field('from_date');
                        frappe.throw(__("Application Period has been Expired for the selected Dates"));
                    }
                }
            })
        }
    },
    // on_submit: function(frm){
    //     if(frm.doc.status == "Approved"){
    //         frappe.call({
    //             "method": 'hunter_douglas.update_attendance.update_attendance_by_app',
    //             args: {
    //                 "employee": frm.doc.employee,
    //                 "from_date": frm.doc.from_date,
    //                 "to_date": frm.doc.to_date,
    //                 "from_date_session":frm.doc.from_date_session,
    //                 "to_date_session": frm.doc.to_date_session,
    //                 "m_status": "OD"
    //             },
    //             callback: function(r){

    //             }
    //         })
    //     }
    // }

});


