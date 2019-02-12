// Copyright (c) 2019, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Fetch Attendance', {
	refresh:function(frm){
		frm.disable_save()
	},
	fetch: function(frm) {
		frappe.call({
			method:"hunter_douglas.custom.fetch_att_test",
			args:{
				"from_date":frm.doc.from_date,
				"to_date":frm.doc.to_date
			},
			freeze:true,
			freeze_message:"Fetching",
			callback:function(r){
				if(r){
					frappe.msgprint(__("Attendance Fetched"));
				}
			}
		})

	}
});
