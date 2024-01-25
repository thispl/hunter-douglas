// Copyright (c) 2021, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Activity', {
	refresh: function(frm) {
		
		var child1 =frm.doc.activity_table
	
		var len1 = child1.length;
        if (len1 == 0) {
            for (var i = 0; i < 6; i++) {
				var row = frappe.model.add_child(frm.doc, "Activity Table", "activity_table");
            }
			refresh_field("activity_table")
		}
	}

});
frappe.ui.form.on('Activity Table', {
	date:function(frm,cdt,cdn){
		var child = locals[cdt][cdn]
		var a = child.date
		console.log(a)
		var days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
		var d = new Date(a);
		var dayName = days[d.getDay()];
		frappe.model.set_value(child.doctype,child.name,"day",dayName)

		// var options = {weekday :'long'}
		// console.log(new Intl.DateTimeFormat('en-US',options).format(a))
		// var date = new Date(datestr)
		// date.toLocaleDateString(locale,{weekday :'long'} )
		// var  datestr = a
		// var day = getDayName(datestr ,'en-US')
		// console.log( day )
	}



	
	});

