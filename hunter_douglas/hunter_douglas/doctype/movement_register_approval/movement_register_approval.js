// Copyright (c) 2018, VHRS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Movement Register Approval', {
	
	onload: function (frm, cdt, cdn) {
		frappe.breadcrumbs.add("HR");
		$(".grid-add-row").hide();
		$(".grid-remove-rows").hide();
		$(":input[data-fieldname='approved']").addClass('btn-success');
		$(":input[data-fieldname='rejected']").addClass('btn-danger');
		frappe.call({
			"method": "frappe.client.get_list",
			args: {
				"doctype": "Movement Register",
				filters: { "docstatus": 0, "status": "Applied" }
			},
			callback: function (r) {
				if (r.message) {
					$.each(r.message, function (i, d) {
						frappe.call({
							"method": "frappe.client.get",
							args: {
								"doctype": "Movement Register",
								"name": d.name
							},
							callback: function (r) {
								if (r.message) {
									if (frappe.session.user == r.message.approver) {
										var row = frappe.model.add_child(frm.doc, "Movement Register Process", "movement_register_process");
										row.movement_register = r.message.name;
										row.employee_name = r.message.employee_name;
										row.from_time = r.message.from_time
										row.to_time = r.message.to_time;
										var tph = r.message.total_permission_hour
										row.total_hours = Number.parseFloat(tph).toFixed(1);
										row.approver = r.message.approver;
										row.approved = 0;
										row.rejected = 0;
									}
									refresh_field("movement_register_process");
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
				"doctype": "Movement Register",
				filters: { "docstatus": 1, "status": "Approved" }
			},
			callback: function (r) {
				if (r.message) {
					$.each(r.message, function (i, d) {
						frappe.call({
							"method": "frappe.client.get",
							args: {
								"doctype": "Movement Register",
								"name": d.name
							},
							callback: function (r) {
								if (r.message) {
									if (frappe.session.user == r.message.approver) {
										var row = frappe.model.add_child(frm.doc, "Movement Register Approval Process", "movement_register_approval_process");
										row.movement_register = r.message.name;
										row.employee_name = r.message.employee_name;
										row.from_time = r.message.from_time
										row.to_time = r.message.to_time;
										row.total_hours = r.message.total_permission_hour;
										row.approver = r.message.approver;
									}
									refresh_field("movement_register_approval_process");
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
		var grid = frm.fields_dict["movement_register_process"].grid;
		$.each(grid.get_selected_children(), function (i, d) {
			frappe.call({
				"method": "hunter_douglas.custom.update_movement_register",
				"args": {
					"doc": d.movement_register,
					"status": "Approved"
				},
				callback: function (r) {
				}
			})
		})
		frappe.msgprint("Status Updated Successfully");
	},
	rejected: function (frm, cdt, cdn) {
		var grid = frm.fields_dict["movement_register_process"].grid;
		$.each(grid.get_selected_children(), function (i, d) {
			frappe.call({
				"method": "hunter_douglas.custom.update_movement_register",
				"args": {
					"doc": d.movement_register,
					"status": "Rejected"
				},
				callback: function (r) {
				}
			})
		})
		frappe.msgprint("Status Updated Successfully");
	},
	to_time: function (frm) {
		frm.clear_table("movement_register_process");
		frm.clear_table("movement_register_approval_process");
		frappe.call({
			"method": "frappe.client.get_list",
			args: {
				"doctype": "Movement Register",
				filters: { "docstatus": 0, "status": "Applied" }
			},
			callback: function (r) {
				if (r.message) {
					$.each(r.message, function (i, d) {
						frappe.call({
							"method": "frappe.client.get",
							args: {
								"doctype": "Movement Register",
								"name": d.name
							},
							callback: function (r) {
								if (r.message) {
									if ((frappe.session.user == r.message.approver) && ((frm.doc.from_time <= r.message.from_time) && (frm.doc.to_time >= r.message.to_time))) {
										var row = frappe.model.add_child(frm.doc, "Movement Register Process", "movement_register_process");
										row.movement_register = r.message.name;
										row.employee_name = r.message.employee_name;
										row.from_time = r.message.from_time
										row.to_time = r.message.to_time;
										row.total_hours = r.message.total_permission_hour;
										row.approver = r.message.approver;
									}
									refresh_field("movement_register_process");
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
				"doctype": "Movement Register",
				filters: { "docstatus": 1, "status": "Approved" }
			},
			callback: function (r) {
				if (r.message) {
					$.each(r.message, function (i, d) {
						frappe.call({
							"method": "frappe.client.get",
							args: {
								"doctype": "Movement Register",
								"name": d.name
							},
							callback: function (r) {
								if (r.message) {
									if ((frappe.session.user == r.message.approver) && ((frm.doc.from_time <= r.message.from_time) && (frm.doc.to_time >= r.message.to_time))) {
										var row = frappe.model.add_child(frm.doc, "Movement Register Approval Process", "movement_register_approval_process");
										row.movement_register = r.message.name;
										row.employee_name = r.message.employee_name;
										row.from_time = r.message.from_time
										row.to_time = r.message.to_time;
										row.total_hours = r.message.total_permission_hour;
										row.approver = r.message.approver;
									}
									refresh_field("movement_register_approval_process");
								}
							}
						})
					})
				}
			}
		})

	}

})