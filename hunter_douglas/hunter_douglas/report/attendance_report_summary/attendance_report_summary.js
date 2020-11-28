// Copyright (c) 2016, VHRS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Attendance Report Summary"] = {
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
			"fieldname": "employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee"
		},
		{
			"fieldname": "department",
			"label": __("Department"),
			"fieldtype": "Link",
			"options": "Department"
		},
		{
			"fieldname": "location",
			"label": __("Location"),
			"fieldtype": "Link",
			"options": "Location"
		},
		// {
		// 	"fieldname": "status_absent",
		// 	"label": __("Absent"),
		// 	"fieldtype": "Check"
		// },
		// {
		// 	"fieldname": "status_in",
		// 	"label": __("In"),
		// 	"fieldtype": "Check"
		// },
		{
			"fieldname": "user",
			"label": __("Employee"),
			"fieldtype": "Data",
			"default": frappe.session.user,
			"hidden": 1

		},

	],

	"formatter": function (row, cell, value, columnDef, dataContext, default_formatter) {
		value = default_formatter(row, cell, value, columnDef, dataContext);
		if (columnDef.id == "Name") {
			// if (dataContext["Session1"] == "AB") {
				columnDef.df.link_onclick =
			"frappe.query_reports['Attendance recapitulation'].open_att_adjust(" + JSON.stringify(dataContext) + ")";
			// }			
		}

		if (columnDef.id == "Session1") {
			if (dataContext["Session1"] === "AB") {
				columnDef.df.link_onclick =
				"frappe.query_reports['Attendance recapitulation'].open_att_adjust(" + JSON.stringify(dataContext) + ")";
				value = '<span style="color:red!important;font-weight:bold">' + value + "</a></span>";
			}
			if (dataContext["Session1"] === "PR") {
				value = "<span style='color:green!important;font-weight:bold'>" + value + "</span>";
			}
			if (dataContext["Session1"] === "CL") {
				value = "<span style='color:green!important;font-weight:bold'>" + value + "</span>";
			}
		}
		if (columnDef.id == "Session2") {
			if (dataContext["Session2"] === "AB") {
				value = "<span style='color:red!important;font-weight:bold'>" + value + "</span>";
			}
			if (dataContext["Session2"] === "PR") {
				value = "<span style='color:green!important;font-weight:bold'>" + value + "</span>";
			}
			if (dataContext["Session2"] === "CL" || dataContext["Session2"] === "PL" || dataContext["Session2"] === "SL") {
				value = "<span style='color:blue!important;font-weight:bold'>" + value + "</span>";
			}
		}
		return value;
	},
	"open_att_adjust": function (data) {
		var d = new frappe.ui.Dialog({
			'fields': [
				{'fieldname': 'ht', 'fieldtype': 'HTML'},
				{'fieldname': 'present', 'fieldtype': 'Check'},
				{fieldtype: "Column Break", fieldname: "cb1", label: __(""), reqd: 0},
				{fieldtype: "Time", fieldname: "in_time", label: __("In Time"), default: data['In Time'],reqd: 0},
				{fieldtype: "Column Break", fieldname: "cb2", label: __(""), reqd: 0},
				{fieldtype: "Time", fieldname: "out_time", label: __("Out Time"), default: data['Out Time'],reqd: 0}

			],
			primary_action: function(){
				var status = d.get_values()
				if (status.present){
					frappe.call({
						method:"hunter_douglas.custom.att_adjust",
						args: {
							'employee': data['Employee'],
							'attendance_date':data['Attendance Date'],
							'name': data['Name']
						},
						callback:function(r){
							frappe.query_report.refresh();
							show_alert(__("Attendance Updated"))
							d.hide()	
						}
					})
				}
				else{
					d.hide()
				}			
			}
		});
		d.fields_dict.ht.$wrapper.html('Mark Present?');
		d.show();
	},

	"onload": function () {
		return frappe.call({
			method: "hunter_douglas.hunter_douglas.report.attendance_recapitulation.attendance_recapitulation.get_filter_dates",
			callback: function (r) {
				var from_date_filter = frappe.query_report_filters_by_name.from_date;
				var to_date_filter = frappe.query_report_filters_by_name.to_date;
				from_date_filter.df.default = r.message[0];
				to_date_filter.df.default = r.message[1];
				from_date_filter.refresh();
				to_date_filter.refresh();
				from_date_filter.set_input(from_date_filter.df.default);
				to_date_filter.set_input(to_date_filter.df.default);
			}
		});
	}
}