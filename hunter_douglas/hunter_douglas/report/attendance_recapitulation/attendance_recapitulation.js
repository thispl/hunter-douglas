// Copyright (c) 2016, VHRS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Attendance recapitulation"] = {
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

	"formatter": function(row, value, column, data, default_formatter) {
		value = default_formatter(row, value, column, data);
		if (column.id === "session1" && frappe.user.has_role("System Manager")) {
		  value = data.session1;
		  column.link_onclick = "frappe.query_reports['Attendance recapitulation'].open_att_adjust1(" + JSON.stringify(data) + ")";
		  
		// if (data["session1"] === "AB") {
		// var con = JSON.stringify(data);
		// value = '<a onclick="frappe.query_reports[\'Attendance recapitulation\'].open_att_adjust1(' + con + ')"><span style="color:red!important;font-weight:bold">' + value + '</a></span>';
		// }
		// if (data["session1"] === "PR") {
		// value = "<span style='color:green!important;font-weight:bold'>" + value + "</span>";
		// }
		// if (data["session1"] === "CL") {
		// value = "<span style='color:green!important;font-weight:bold'>" + value + "</span>";
		// }

		}
		if (column.id === "name" && frappe.user.has_role("Employee")) {
		  value = data.name;
		  column.link_onclick = "frappe.query_reports['Attendance recapitulation'].open_att_adjust1(" + JSON.stringify(data) + ")";
		}

		if (column.id === "shift" && frappe.user.has_role("System Manager")) {
		  value = data.shift;
		  column.link_onclick = "frappe.query_reports['Attendance recapitulation'].open_att_adjust2(" + JSON.stringify(data) + ")";
		}
	
		value = default_formatter(value, row, column, data);
		
		if (column.id === "session1") {
		  if (data["session1"] === "AB") {
			var con = JSON.stringify(data);
			value = '<a onclick="frappe.query_reports[\'Attendance recapitulation\'].open_att_adjust1(' + con + ')"><span style="color:red!important;font-weight:bold">' + value + '</a></span>';
		  }
		  if (data["session1"] === "PR") {
			value = "<span style='color:green!important;font-weight:bold'>" + value + "</span>";
		  }
		  if (data["session1"] === "CL") {
			value = "<span style='color:green!important;font-weight:bold'>" + value + "</span>";
		  }
		}
	
		if (column.id === "session2") {
		  if (data["session2"] === "AB") {
			var con = JSON.stringify(data);
			value = '<a onclick="frappe.query_reports[\'Attendance recapitulation\'].open_att_adjust1(' + con + ')"><span style="color:red!important;font-weight:bold">' + value + "</a></span>";
		  }
		  if (data["session2"] === "PR") {
			value = "<span style='color:green!important;font-weight:bold'>" + value + "</span>";
		  }
		  if (data["session2"] === "CL" || data["session2"] === "PL" || data["session2"] === "SL") {
			value = "<span style='color:blue!important;font-weight:bold'>" + value + "</span>";
		  }
		}
		return value;
	  },
	
	"open_att_adjust": function(data) {
		if (data['In Time'] === '-') {
			data['In Time'] = '';
		}
		if (data['Out Time'] === '-') {
			data['Out Time'] = '';
		}
		var in_out_time = '';
		var d = new frappe.ui.Dialog({
			'fields': [
				{ 'fieldname': 'ht', 'fieldtype': 'HTML' },
				{ label: "Mark P", 'fieldname': 'present', 'fieldtype': 'Check' },
				{ label: "Mark AB", 'fieldname': 'absent', 'fieldtype': 'Check' },
				// { label: "Mark PH", 'fieldname': 'ph', 'fieldtype': 'Check' },
				// { label: "Mark WO", 'fieldname': 'wo', 'fieldtype': 'Check' },
				{ label: "Mark CL", 'fieldname': 'cl', 'fieldtype': 'Check' },
				{ label: "Mark PL", 'fieldname': 'pl', 'fieldtype': 'Check' },
				{ label: "Mark SL", 'fieldname': 'sl', 'fieldtype': 'Check' },
				{ label: "Mark EL", 'fieldname': 'el', 'fieldtype': 'Check' },
				// { label: "Mark HD", 'fieldname': 'hd', 'fieldtype': 'Check' },
				{ 'fieldname': 'it', 'fieldtype': 'Time', 'label': 'In Time', 'default': data['In Time'] },
				{ 'fieldname': 'ot', 'fieldtype': 'Time', 'label': 'Out Time', 'default': data['Out Time'] },
				{ 'fieldname': 'is', 'fieldtype': 'Section Break', 'label': 'In - Out Time' },
				{ 'fieldname': 'lat', 'fieldtype': 'Data', 'label': 'Late Time', 'default': data['Late Time'] },
				{ 'fieldname': 'es', 'fieldtype': 'Section Break', 'label': 'Early - Status' },
				{ 'fieldname': 'ep', 'fieldtype': 'Data', 'label': 'Early Time', 'default': data['Early Time'] },
				{ 'fieldname': 'eo', 'fieldtype': 'Data', 'label': 'Early Out Time', 'default': data['Early Out Time'] },
				{ 'fieldname': 'op', 'fieldtype': 'Select', 'label': 'Late Count', 'default': data['Late Count'], 'options': '\n1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n11\n12\n13\n14\n15\n16\n17\n18\n19\n20\n21\n22\n23\n24\n25\n26\n27\n28\n29\n30' },
				{ 'fieldname': 'oth', 'fieldtype': 'Select', 'label': 'Over Time Hours', 'default': data['Over Time Hours'], 'options': '\n0\n1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n11\n12' },
				{ 'fieldname': 'otm', 'fieldtype': 'Time', 'label': 'Over Time Min', 'default': data['Over Time Min'] }
			],
			primary_action_label: 'Save',
			primary_action: function() {
				var values = d.get_values();
				frappe.call({
					method: 'hunter_douglas.mark_recapitulation.update_attendance',
					args: {
						data: values,
						action: 'update', 																																																																																																																																																																																																										 
						employee: data['employee'],
						name:data['name']
					},
					callback: function(r) {
						if (r.message === 'success') {
							frappe.query_reports['Attendance recapitulation'].refresh();
							d.hide();
						}
					}
				});
			}
		});
		var wrapper = $('<div class="row"></div>');
		var in_time = $('<div class="col-sm-4"></div>').append('<label for="name">' + 'In Time' + '</label><input class="form-control" type="time" id="txtin" placeholder="' + 'In Time' + '" />');
		var out_time = $('<div class="col-sm-4"></div>').append('<label for="name">' + 'Out Time' + '</label><input class="form-control" type="time" id="txtout" placeholder="' + 'Out Time' + '" />');
		wrapper.append(in_time);
		wrapper.append(out_time);
		d.fields_dict.ht.$wrapper.empty().append(wrapper);
	
		d.set_values(data);
		d.show();
	},
	
	"open_att_adjust1": function(data) {
		console.log('hi')
		console.log(data)
		console.log('hii')
		if (data['In Time'] === '-') {
			data['In Time'] = '';
		}
		if (data['Out Time'] === '-') {
			data['Out Time'] = '';
		}
		var in_out_time = '';
		var d = new frappe.ui.Dialog({
			'fields': [
				{ 'fieldname': 'ht', 'fieldtype': 'HTML' },
				{ label: "Mark P", 'fieldname': 'present', 'fieldtype': 'Check' },
				{ label: "Mark AB", 'fieldname': 'absent', 'fieldtype': 'Check' },
				// { label: "Mark PH", 'fieldname': 'ph', 'fieldtype': 'Check' },
				// { label: "Mark WO", 'fieldname': 'wo', 'fieldtype': 'Check' },
				{ label: "Mark CL", 'fieldname': 'cl', 'fieldtype': 'Check' },
				{ label: "Mark PL", 'fieldname': 'pl', 'fieldtype': 'Check' },
				{ label: "Mark SL", 'fieldname': 'sl', 'fieldtype': 'Check' },
				{ label: "Mark EL", 'fieldname': 'el', 'fieldtype': 'Check' },
				// { label: "Mark HD", 'fieldname': 'hd', 'fieldtype': 'Check' },
				{ 'fieldname': 'it', 'fieldtype': 'Time', 'label': 'In Time', 'default': data['In Time'] },
				{ 'fieldname': 'ot', 'fieldtype': 'Time', 'label': 'Out Time', 'default': data['Out Time'] },
				{ 'fieldname': 'is', 'fieldtype': 'Section Break', 'label': 'In - Out Time' },
				{ 'fieldname': 'lat', 'fieldtype': 'Data', 'label': 'Late Time', 'default': data['Late Time'] },
				{ 'fieldname': 'es', 'fieldtype': 'Section Break', 'label': 'Early - Status' },
				{ 'fieldname': 'ep', 'fieldtype': 'Data', 'label': 'Early Time', 'default': data['Early Time'] },
				{ 'fieldname': 'eo', 'fieldtype': 'Data', 'label': 'Early Out Time', 'default': data['Early Out Time'] },
				{ 'fieldname': 'op', 'fieldtype': 'Select', 'label': 'Late Count', 'default': data['Late Count'], 'options': '\n1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n11\n12\n13\n14\n15\n16\n17\n18\n19\n20\n21\n22\n23\n24\n25\n26\n27\n28\n29\n30' },
				{ 'fieldname': 'oth', 'fieldtype': 'Select', 'label': 'Over Time Hours', 'default': data['Over Time Hours'], 'options': '\n0\n1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n11\n12' },
				{ 'fieldname': 'otm', 'fieldtype': 'Time', 'label': 'Over Time Min', 'default': data['Over Time Min'] }
			],
			primary_action_label: 'Save',
			primary_action: function() {
				var values = d.get_values();
				frappe.call({
					method: 'hunter_douglas.mark_recapitulation.update_attendance',
					args: {
						data: values,
						action: 'update',
						employee: data['employee'],
						name:data['name']
					},
					callback: function(r) {
						if (r.message) {
							if(r.message == "Present"){
								console.log(value)
							// frm.set_value(data["session1"],"PR")
							}
							// frappe.query_reports['Attendance recapitulation'].refresh();
							// d.hide();
						}
					}
				});
			}
		});
		var wrapper = $('<div class="row"></div>');
		var in_time = $('<div class="col-sm-4"></div>').append('<label for="name">' + 'In Time' + '</label><input class="form-control" type="time" id="txtin" placeholder="' + 'In Time' + '" />');
		var out_time = $('<div class="col-sm-4"></div>').append('<label for="name">' + 'Out Time' + '</label><input class="form-control" type="time" id="txtout" placeholder="' + 'Out Time' + '" />');
		wrapper.append(in_time);
		wrapper.append(out_time);
		d.fields_dict.ht.$wrapper.empty().append(wrapper);
	
		d.set_values(data);
		d.show();
	},
	
	"open_att_adjust2": function(data) {
		if (data['In Time'] === '-') {
			data['In Time'] = '';
		}
		if (data['Out Time'] === '-') {
			data['Out Time'] = '';
		}
		var in_out_time = '';
		var d = new frappe.ui.Dialog({
			'fields': [
				{ 'fieldname': 'ht', 'fieldtype': 'HTML' },
				{ label: "Mark P", 'fieldname': 'present', 'fieldtype': 'Check' },
				{ label: "Mark AB", 'fieldname': 'absent', 'fieldtype': 'Check' },
				// { label: "Mark PH", 'fieldname': 'ph', 'fieldtype': 'Check' },
				// { label: "Mark WO", 'fieldname': 'wo', 'fieldtype': 'Check' },
				{ label: "Mark CL", 'fieldname': 'cl', 'fieldtype': 'Check' },
				{ label: "Mark PL", 'fieldname': 'pl', 'fieldtype': 'Check' },
				{ label: "Mark SL", 'fieldname': 'sl', 'fieldtype': 'Check' },
				{ label: "Mark EL", 'fieldname': 'el', 'fieldtype': 'Check' },
				// { label: "Mark HD", 'fieldname': 'hd', 'fieldtype': 'Check' },
				{ 'fieldname': 'it', 'fieldtype': 'Time', 'label': 'In Time', 'default': data['In Time'] },
				{ 'fieldname': 'ot', 'fieldtype': 'Time', 'label': 'Out Time', 'default': data['Out Time'] },
				{ 'fieldname': 'is', 'fieldtype': 'Section Break', 'label': 'In - Out Time' },
				{ 'fieldname': 'lat', 'fieldtype': 'Data', 'label': 'Late Time', 'default': data['Late Time'] },
				{ 'fieldname': 'es', 'fieldtype': 'Section Break', 'label': 'Early - Status' },
				{ 'fieldname': 'ep', 'fieldtype': 'Data', 'label': 'Early Time', 'default': data['Early Time'] },
				{ 'fieldname': 'eo', 'fieldtype': 'Data', 'label': 'Early Out Time', 'default': data['Early Out Time'] },
				{ 'fieldname': 'op', 'fieldtype': 'Select', 'label': 'Late Count', 'default': data['Late Count'], 'options': '\n1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n11\n12\n13\n14\n15\n16\n17\n18\n19\n20\n21\n22\n23\n24\n25\n26\n27\n28\n29\n30' },
				{ 'fieldname': 'oth', 'fieldtype': 'Select', 'label': 'Over Time Hours', 'default': data['Over Time Hours'], 'options': '\n0\n1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n11\n12' },
				{ 'fieldname': 'otm', 'fieldtype': 'Time', 'label': 'Over Time Min', 'default': data['Over Time Min'] }
			],
			primary_action_label: 'Save',
			primary_action: function() {
				var values = d.get_values();
				frappe.call({
					method: 'hunter_douglas.mark_recapitulation.update_attendance',
					args: {
						data: values,
						action: 'update',
						employee: data['employee'],
						name:data['name'],
						date:data["attendance_date"]
					},
					callback: function(r) {
						if (r.message === 'success') {
							frappe.query_reports['Attendance recapitulation'].refresh();
							d.hide();
						}
					}
				});
			}
		});
		var wrapper = $('<div class="row"></div>');
		var in_time = $('<div class="col-sm-4"></div>').append('<label for="name">' + 'In Time' + '</label><input class="form-control" type="time" id="txtin" placeholder="' + 'In Time' + '" />');
		var out_time = $('<div class="col-sm-4"></div>').append('<label for="name">' + 'Out Time' + '</label><input class="form-control" type="time" id="txtout" placeholder="' + 'Out Time' + '" />');
		wrapper.append(in_time);
		wrapper.append(out_time);
		d.fields_dict.ht.$wrapper.empty().append(wrapper);
	
		d.set_values(data);
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