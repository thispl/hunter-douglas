// Copyright (c) 2016, VHRS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Attendance Summary Data"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.month_start(),
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname":"user",
			"label": __("Employee"),
			"fieldtype": "Data",
			"default": frappe.session.user,
			"hidden":1
			
		},				
						
	],

	"formatter": function (row, cell, value, columnDef, dataContext, default_formatter) {
		value = default_formatter(row, cell, value, columnDef, dataContext);
		if (dataContext["Status"] === "Absent") {
			value = "<span style='color:red!important;font-weight:bold'>" + value + "</span>";
		}
		return value;
	},
	"onload": function() {
		console.log(frappe.datetime.nowdate())
	}
}