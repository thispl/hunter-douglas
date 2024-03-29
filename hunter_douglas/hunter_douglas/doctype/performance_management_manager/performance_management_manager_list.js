frappe.listview_settings['Performance Management Manager'] = {
    onload:function(me){
        if(!frappe.user.has_role("System Manager")){
            var d  = new Date()
            var apy = d.getFullYear() - 1
            frappe.route_options = {
                "appraisal_year": ["=", apy],
                "manager": ["=", frappe.session.user]
            };
        }
    },
    refresh: function (me) {
       
        me.page.sidebar.find(".list-link[data-view='Kanban']").addClass("hide");
        me.page.sidebar.find(".list-link[data-view='Tree']").addClass("hide");
        me.page.sidebar.find(".assigned-to-me a").addClass("hide");
        if(!frappe.user.has_role("System Manager")){
            if (!frappe.route_options) {  
                frappe.route_options = {
                    "manager": ["=", frappe.session.user]
                };
            }
        }
    }

};