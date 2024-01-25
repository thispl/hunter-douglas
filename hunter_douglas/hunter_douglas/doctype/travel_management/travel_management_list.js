frappe.listview_settings['Travel Management'] = {
    // onload:function(listview){
    //     listview.page.add_menu_item(__("Approve"),function(){
    //         method = "hunter_douglas.custom.bulk_travel_approve"
    //         listview.call_for_selected_items(method,{'status':'Approved'});
    //     }),
    //     listview.page.add_menu_item(__("Reject"),function(){
    //         method = "hunter_douglas.custom.bulk_travel_approve"
    //         listview.call_for_selected_items(method,{'status':'Rejected'});
    //     })
    // },
    onload:function(me){
		me.page.sidebar.find(".list-link[data-view='Kanban']").addClass("hide");
		me.page.sidebar.find(".list-link[data-view='Tree']").addClass("hide");
		me.page.sidebar.find(".assigned-to-me a").addClass("hide");
		if(!frappe.user.has_role("Travel Desk")){
			if(!frappe.user.has_role('System Manager')){

			// 
			frappe.model.get_value('Employee', { 'user_id': frappe.session.user }, 'employee_number',
            function (data) {
                console.log(data)
                // if (data) {
                //     me.filter_area.add([[me.doctype, "employee", '=', data.employee_number]]);
                //     $('*[data-fieldname="employee"]').find('.input-with-feedback').attr('readonly',true);
                // }
            })
		}
	}
	}
    
};