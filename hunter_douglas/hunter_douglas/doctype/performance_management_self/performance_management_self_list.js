frappe.listview_settings['Performance Management Self'] = {
    // onload:function(frm){
    //     frm.trigger("refresh")
    // },
    refresh: function (me) {
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
    }

};