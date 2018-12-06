// Copyright (c) 2016, VHRS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Late - IN Register"] = {
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
			"reqd": 1
		},
	],
		// get_chart_data: function (columns, result) {
		// 	return {
		// 		data: {
		// 			labels: result.map(d => d[0]),
		// 			datasets: [{
		// 				title: 'Mins to first response',
		// 				values: result.map(d => d[1])
		// 			}]
		// 		},
		// 		type: 'line',
		// 	}
		// },
		"formatter":function (row, cell, value, columnDef, dataContext, default_formatter) {
			value = default_formatter(row, cell, value, columnDef, dataContext);
		   for(i=1;i<31;i++){
			if (columnDef.id == i && dataContext[i] > 0) {
					value = "<span style='color:black!important;font-weight:bold'>" + value + "</span>";
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
