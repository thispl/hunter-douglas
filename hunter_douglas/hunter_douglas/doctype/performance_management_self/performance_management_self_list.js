frappe.listview_settings['Performance Management Self'] = {
    // onload:function(frm){
    //     frm.trigger("refresh")
    // },
    refresh: function (me) {
        var emp = ""
        me.page.sidebar.find(".list-link[data-view='Kanban']").addClass("hide");
        me.page.sidebar.find(".list-link[data-view='Tree']").addClass("hide");
        me.page.sidebar.find(".assigned-to-me a").addClass("hide");
        frappe.model.get_value('Employee', { 'user_id': frappe.session.user }, 'employee_number',
            function (data) {
                if (data) {
                    me.filter_list.add_filter(me.doctype, "employee_code", '=', data.employee_number);
                    me.run()
                }
            })
            
            frappe.call({
            "method": "frappe.client.get_list",
            args:{
                doctype: "Employee",
                filters: {"user_id": frappe.session.user}
            },
            callback: function(r){
                emp = r.message[0].name  
                if(!frappe.user.has_role("System Manager")){
                    if (!frappe.route_options) {            
                        frappe.route_options = {
                            "employee_code1": ["=", emp]
                        };                       
                    }
                }
            }
        })
        
    }
    



};