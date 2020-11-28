// Copyright (c) 2016, VHRS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Attendance Register Report"] = {
	"filters": [
		{
			"fieldname":"month",
			"label": __("Month"),
			"fieldtype": "Select",
			"options": "Jan\nFeb\nMar\nApr\nMay\nJun\nJul\nAug\nSep\nOct\nNov\nDec",
			"default": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
				"Dec"][frappe.datetime.str_to_obj(frappe.datetime.get_today()).getMonth()],
		},
		{
			"fieldname":"year",
			"label": __("Year"),
			"fieldtype": "Select",
			// "options": "2018\n2019",
			"reqd": 1
		},
		{
			"fieldname":"employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options":"Employee"
		},
		{
			"fieldname":"department",
			"label": __("Department"),
			"fieldtype": "Link",
			"options":"Department"
		},
		{
			"fieldname":"location",
			"label": __("Location"),
			"fieldtype": "Link",
			"options":"Location"
		},
	],
	
	"formatter": function (row, cell, value, columnDef, dataContext, default_formatter) {
		value = default_formatter(row, cell, value, columnDef, dataContext);
		for(i=0;i<32;i++)
		{
		if (columnDef.id == i) {
			if (dataContext[i] === "AB") {
				value = "<span style='color:red!important;font-weight:bold'>" + value + "</span>";
			}
			if (dataContext[i] === "PR") {
				value = "<span style='color:green!important;font-weight:bold'>" + value + "</span>";
			}
			if (dataContext[i] === "PL") {
				value = "<span style='color:blue!important;font-weight:bold'>" + value + "</span>";
			}
		}

		if (columnDef.id == i) {
			if (dataContext[i] === "AB") {
				value = "<span style='color:red!important;font-weight:bold'>" + value + "</span>";
			}
			if (dataContext[i] === "PR") {
				value = "<span style='color:green!important;font-weight:bold'>" + value + "</span>";
			}
			if (dataContext[i] === "CL" || dataContext["Session2"] === "PL" || dataContext["Session2"] === "SL") {
				value = "<span style='color:blue!important;font-weight:bold'>" + value + "</span>";
			}
		}
	}
		return value;
	},
	"onload": function() {
		return  frappe.call({
			method: "erpnext.hr.report.monthly_attendance_sheet.monthly_attendance_sheet.get_attendance_years",
			callback: function(r) {
				var year_filter = frappe.query_report_filters_by_name.year;
				year_filter.df.options = r.message;
				year_filter.df.default = r.message.split("\n")[0];
				year_filter.refresh();
				year_filter.set_input(year_filter.df.default);
			}
		});
	}
}
