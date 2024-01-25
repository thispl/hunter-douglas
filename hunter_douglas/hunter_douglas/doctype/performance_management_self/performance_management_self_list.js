frappe.listview_settings['Performance Management Self'] = {
    onload:function(listview){
        frappe.model.get_value('Employee', { 'user_id': frappe.session.user }, 'employee_number',
            function (data) {
                if (data) {
                    listview.filter_area.clear()
                    listview.filter_area.add([[listview.doctype, "employee_code", '=', data.employee_number]]);
                    listview.filter_area.add([[listview.doctype, "appraisal_year", '=', "2022"]]);
                    listview.refresh();     }
            })
    },
    }
//     onload: function (me) {
       
//         var emp = ""
//         me.page.sidebar.find(".list-link[data-view='Kanban']").addClass("hide");
//         me.page.sidebar.find(".list-link[data-view='Kanban']").addClass("hide");
//         me.page.sidebar.find(".assigned-to-me a").addClass("hide");

//         frappe.model.get_value('Employee', { 'user_id': frappe.session.user }, 'employee_number',
//             function (data) {
//                 if (data) {
//                     me.filter_list.add_filter(me.doctype, "employee_code", '=', data.employee_number);
//                     me.run()
//                 }
//             })

//         frappe.call({
//             "method": "frappe.client.get_list",
//             args: {
//                 doctype: "Employee",
//                 filters: { "user_id": frappe.session.user }
//             },
//             callback: function (r) {
//                 emp = r.message[0].name
//                 var d = new Date()
//                 apy = String(d.getFullYear() - 1)
//                 frappe.model.get_value('Performance Management Self', { 'appraisal_year': apy,'employee_code':emp }, 'name',
//                     function (data) {
//                         if (Object.keys(data).length >= 1) {
//                             me.page.btn_primary.hide()
//                         }
//                     })
//                 if (!frappe.user.has_role("System Manager")) {
//                     var d = new Date()
//                     var apy = d.getFullYear() - 1
//                     me.filter_area.add([[me.doctype, "employee_code1", '=', emp]]);
//                     me.filter_area.add([[me.doctype, "appraisal_year", '=', apy]]);
//                     // if (!frappe.route_options) {
//                     //     frappe.route_options = {
//                     //         "employee_code1": ["=", emp],
//                     //         "appraisal_year": ["=", apy]
//                     //     };
//                     // }
//                 }
//             }
//         })

//     }




// };