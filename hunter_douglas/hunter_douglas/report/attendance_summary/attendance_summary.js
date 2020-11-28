frappe.query_reports["Attendance Summary"] = {
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
	
}