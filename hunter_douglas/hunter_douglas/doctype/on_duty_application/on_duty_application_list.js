frappe.listview_settings['On Duty Application'] = {
	add_fields: ["status"],
	get_indicator: function(doc) {
		return [__(doc.status), frappe.utils.guess_colour(doc.status),
			"status,=," + doc.status];
	},
    // onload:function(listview){
	// 	frappe.model.get_value('Employee', { 'user_id': frappe.session.user }, 'employee_number',
    //         function (data) {
    //             if (data) {
    //                 me.filter_list.add_filter(me.doctype, "employee", '=', data.employee_number);
    //                 me.run()
    //             }
    //         })
    //     listview.page.add_menu_item(__("Approve"),function(){
    //         method = "hunter_douglas.custom.bulk_onduty_approve"
    //         listview.call_for_selected_items(method,{'status':'Approved'});
    //     }),
    //     listview.page.add_menu_item(__("Reject"),function(){
    //         method = "hunter_douglas.custom.bulk_on_duty_approve"
    //         listview.call_for_selected_items(method,{'status':'Rejected'});
    //     })
	// },
	
	
    onload:function(me){
		me.page.sidebar.find(".list-link[data-view='Kanban']").addClass("hide");
		me.page.sidebar.find(".list-link[data-view='Tree']").addClass("hide");
        me.page.sidebar.find(".assigned-to-me a").addClass("hide");
        if(!frappe.user.has_role('System Manager')){
		$('*[data-fieldname="employee"]').find('.input-with-feedback').attr('readonly',true);
		frappe.model.get_value('Employee', { 'user_id': frappe.session.user }, 'employee_number',
            function (data) {
                if (data) {
					me.filter_area.add([[me.doctype, "employee", '=', data.employee_number]]);
                }
            })
    }
}
    
};