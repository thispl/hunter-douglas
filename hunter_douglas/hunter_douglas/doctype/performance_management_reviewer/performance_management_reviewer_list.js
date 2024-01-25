frappe.listview_settings['Performance Management Reviewer'] = {
    onload:function(listview){
        frappe.model.get_value('Employee', { 'user_id': frappe.session.user }, 'employee_number',
        function (data) {
            if (data) {
                listview.filter_area.clear()
                // listview.filter_area.add([[listview.doctype, "employee_code", '=', data.employee_number]]);
                listview.filter_area.add([[listview.doctype, "appraisal_year", '=', "2022"]]);
                listview.refresh();     }
        })
        if(!frappe.user.has_role("System Manager")){
            var d  = new Date()
            var apy = d.getFullYear() - 1
            frappe.route_options = {
                "appraisal_year": ["=", apy],
            };
        }
    },
    refresh: function (me) {
    //     if(!frappe.user.has_role("System Manager")){
    //     d = new Date()
    //     var apy = d.getFullYear() - 1
    //     console.log(apy)
    //     frappe.route_options = {
    //         "appraisal_year": ["=", apy],
    //     };
    // }
        me.page.sidebar.find(".list-link[data-view='Kanban']").addClass("hide");
        me.page.sidebar.find(".list-link[data-view='Tree']").addClass("hide");
        me.page.sidebar.find(".assigned-to-me a").addClass("hide");
        // if(!frappe.user.has_role("System Manager")){
        //     if (!frappe.route_options) {
        //         frappe.route_options = {
        //             "reviewer": ["=", frappe.session.user]
        //         };
        //     }
        // }
    }

};