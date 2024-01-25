// Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */
if(frappe.session.user = 'hr.hdi@hunterdouglas.asia'){
	frappe.query_reports["Attendance Register"] = {
		"filters": [
			{
				"fieldname": "from_date",
				"label": __("From Date"),
				"fieldtype": "Date",
				"reqd": 1
			},
			{
				"fieldname": "to_date",
				"label": __("To Date"),
				"fieldtype": "Date",
				"reqd": 1
			},
			{
				"fieldname": "employee",
				"label": __("Employee"),
				"fieldtype": "Link",
				"options": "Employee",
			},
			{
				"fieldname": "department",
				"label": __("Department"),
				"fieldtype": "Link",
				"options": "Department",
			},
			{
				"fieldname": "location_name",
				"label": __("Location"),
				"fieldtype": "Link",
				"options": "Location",
		
			},	
		],
		onload: function (report) {
			var to_date = frappe.query_report.get_filter('to_date');
			to_date.refresh();
			to_date.set_input(frappe.datetime.add_days(frappe.datetime.month_start(),30))
			var from_date = frappe.query_report.get_filter('from_date');
			from_date.refresh();
			var d = frappe.datetime.add_months(frappe.datetime.month_start())
			from_date.set_input(frappe.datetime.add_days(d))
		},
	};
}
else if(frappe.session.user = 'hr.hdi@hunterdouglas.in'){
	frappe.query_reports["Attendance Register"] = {
		"filters": [
			{
				"fieldname": "from_date",
				"label": __("From Date"),
				"fieldtype": "Date",
				"reqd": 1
			},
			{
				"fieldname": "to_date",
				"label": __("To Date"),
				"fieldtype": "Date",
				"reqd": 1
			},
			{
				"fieldname": "employee",
				"label": __("Employee"),
				"fieldtype": "Link",
				"options": "Employee",
			},
			{
				"fieldname": "department",
				"label": __("Department"),
				"fieldtype": "Link",
				"options": "Department",
			},
			{
				"fieldname": "location_name",
				"label": __("Location"),
				"fieldtype": "Link",
				"options": "Location",
		
			},	
		],
		onload: function (report) {
			var to_date = frappe.query_report.get_filter('to_date');
			to_date.refresh();
			to_date.set_input(frappe.datetime.add_days(frappe.datetime.month_start(),30))
			var from_date = frappe.query_report.get_filter('from_date');
			from_date.refresh();
			var d = frappe.datetime.add_months(frappe.datetime.month_start())
			from_date.set_input(frappe.datetime.add_days(d))
		},
	};
}
else{
	frappe.query_reports["Attendance Register"] = {
		"filters": [
			{
				"fieldname": "from_date",
				"label": __("From Date"),
				"fieldtype": "Date",
				"reqd": 1,
				"read_only":1,
			},
			{
				"fieldname": "to_date",
				"label": __("To Date"),
				"fieldtype": "Date",
				"reqd": 1,
				"read_only":1,
			}
		],
		onload: function (report) {
			var to_date = frappe.query_report.get_filter('to_date');
			to_date.refresh();
			to_date.set_input(frappe.datetime.add_days(frappe.datetime.month_start(),30))
			var from_date = frappe.query_report.get_filter('from_date');
			from_date.refresh();
			var d = frappe.datetime.add_months(frappe.datetime.month_start())
			from_date.set_input(frappe.datetime.add_days(d))
		},
	}
}