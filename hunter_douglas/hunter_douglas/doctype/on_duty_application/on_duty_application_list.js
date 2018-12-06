frappe.listview_settings['On Duty Application'] = {
    onload:function(listview){
        listview.page.add_menu_item(__("Approve"),function(){
            method = "hunter_douglas.custom.bulk_onduty_approve"
            listview.call_for_selected_items(method,{'status':'Approved'});
        }),
        listview.page.add_menu_item(__("Reject"),function(){
            method = "hunter_douglas.custom.bulk_on_duty_approve"
            listview.call_for_selected_items(method,{'status':'Rejected'});
        })
    }
    
};