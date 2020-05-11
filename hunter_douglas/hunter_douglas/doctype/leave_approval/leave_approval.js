// Copyright (c) 2018, VHRS and contributors
// For license information, please see license.txt
frappe.ui.form.on('Leave Approval', {
	onload: function (frm, cdt, cdn) {
		frappe.breadcrumbs.add("HR");
		$(".grid-add-row").hide();
		$(".grid-remove-rows").hide();
		$(":input[data-fieldname='approved']").addClass('btn-success');
		$(":input[data-fieldname='rejected']").addClass('btn-danger');
		frappe.call({
			"method": "frappe.client.get_list",
			args: {
				"doctype": "Leave Application",
				filters: { "docstatus": 0, "status": ["in",["Applied","Approved"]] },
				limit_page_length:50
			},
			callback: function (r) {
				if (r.message) {
					$.each(r.message, function (i, d) {
						frappe.call({
							"method": "frappe.client.get",
							args: {
								"doctype": "Leave Application",
								"name": d.name
							},
							callback: function (r) {
								if (r.message) {

									if ((frappe.session.user == r.message.leave_approver) || (frappe.user.has_role("System Manager"))) {
										var row = frappe.model.add_child(frm.doc, "Leave Approval Process", "leave_application_management_process");
										row.leave_application = r.message.name;
										row.employee_name = r.message.employee_name;
										row.from_date = r.message.from_date;
										row.to_date = r.message.to_date;
										row.no_of_days = r.message.total_leave_days;
										row.leave_approver = r.message.leave_approver;
										row.reason = r.message.reason;
										row.leave_type = r.message.leave_type1;
										row.approved = 0;
										row.rejected = 0;
									}
									refresh_field("leave_application_management_process");
								}
							}
						})
					})
				}
			}
		})
		frappe.call({
			"method": "frappe.client.get_list",
			args: {
				"doctype": "Leave Application",
				filters: { "docstatus": 1, "status": "Approved" },
				limit_page_length:50
			},
			callback: function (r) {
				if (r.message) {
					$.each(r.message, function (i, d) {
						frappe.call({
							"method": "frappe.client.get",
							args: {
								"doctype": "Leave Application",
								"name": d.name
							},
							callback: function (r) {
								if (r.message) {
									if ((frappe.session.user == r.message.leave_approver) || (frappe.user.has_role("System Manager"))) {
										var row = frappe.model.add_child(frm.doc, "Leave Approval Process1", "leave_approval_process");
										row.leave_application = r.message.name;
										row.employee_name = r.message.employee_name;
										row.from_date = r.message.from_date;
										row.to_date = r.message.to_date;
										row.no_of_days = r.message.total_leave_days;
										row.leave_approver = r.message.leave_approver;
										row.reason = r.message.reason;
										row.leave_type = r.message.leave_type1;
										row.approved = 0;
										row.rejected = 0;
									}
									refresh_field("leave_approval_process");
								}
							}
						})
					})
				}
			}
		})
	},
	refresh: function (frm) {
		frm.disable_save();
	},
	approved: function (frm, cdt, cdn) {
		var grid = frm.fields_dict["leave_application_management_process"].grid;
		if (grid.get_selected_children().length !== 0) {
			$.each(grid.get_selected_children(), function (i, d) {
				frappe.call({
					"method": "hunter_douglas.custom.update_leave_approval",
					"args": {
						"doc": d.leave_application,
						"status": "Approved"
					},
					callback: function (r) {
					}
				})
			})
			frappe.msgprint("Status Updated Successfully");
			setTimeout(function () { location.reload() }, 3000);

		}
	},
	rejected: function (frm, cdt, cdn) {
		var grid = frm.fields_dict["leave_application_management_process"].grid;
		if (grid.get_selected_children().length !== 0) {
			$.each(grid.get_selected_children(), function (i, d) {
				frappe.call({
					"method": "hunter_douglas.custom.update_leave_approval",
					"args": {
						"doc": d.leave_application,
						"status": "Rejected"
					},
					callback: function (r) {
					}
				})
			})
			frappe.msgprint("Status Updated Successfully");
			setTimeout(function () { location.reload() }, 500);
		}
	},
	to: function (frm) {
		frm.clear_table("leave_application_management_process");
		frm.clear_table("leave_approval_process");
		frappe.call({
			"method": "frappe.client.get_list",
			args: {
				"doctype": "Leave Application",
				filters: { "docstatus": 0, "status": "Applied", "from_date":['>=',frm.doc.from_date],"to_date":['<=',frm.doc.to_date] },
				limit_page_length:50
			},
			callback: function (r) {
				if (r.message) {
					$.each(r.message, function (i, d) {
						frappe.call({
							"method": "frappe.client.get",
							args: {
								"doctype": "Leave Application",
								"name": d.name
							},
							callback: function (r) {
								if (r.message) {
									if ((frappe.session.user == r.message.leave_approver) && ((frm.doc.leave_date_from <= r.message.from_date) && (frm.doc.to >= r.message.to_date)) || (frappe.user.has_role("System Manager"))) {
										var row = frappe.model.add_child(frm.doc, "Leave Approval Process", "leave_application_management_process");
										row.leave_application = r.message.name;
										row.employee_name = r.message.employee_name;
										row.from_date = r.message.from_date;
										row.to_date = r.message.to_date;
										row.no_of_days = r.message.total_leave_days;
										row.leave_approver = r.message.leave_approver;

										row.approved = 0;
										row.rejected = 0;
									}
									refresh_field("leave_application_management_process");
								}
							}
						})
					})
				}
			}
		})
		frappe.call({
			"method": "frappe.client.get_list",
			args: {
				"doctype": "Leave Application",
				filters: { "docstatus": 1, "status": "Approved", "from_date":['>=',frm.doc.from_date],"to_date":['<=',frm.doc.to_date] },
				limit_page_length:50
			},
			callback: function (r) {
				if (r.message) {
					$.each(r.message, function (i, d) {
						frappe.call({
							"method": "frappe.client.get",
							args: {
								"doctype": "Leave Application",
								"name": d.name
							},
							callback: function (r) {
								if (r.message) {
									if ((frappe.session.user == r.message.leave_approver) && ((frm.doc.leave_date_from <= r.message.from_date) && (frm.doc.to >= r.message.to_date)) || (frappe.user.has_role("System Manager"))) {
										var row = frappe.model.add_child(frm.doc, "Leave Approval Process1", "leave_approval_process");
										row.leave_application = r.message.name;
										row.employee_name = r.message.employee_name;
										row.from_date = r.message.from_date;
										row.to_date = r.message.to_date;
										row.no_of_days = r.message.total_leave_days;
										row.leave_approver = r.message.leave_approver;

										row.approved = 0;
										row.rejected = 0;
									}
									refresh_field("leave_approval_process");
								}
							}
						})
					})
				}
			}
		})

	}
})	
