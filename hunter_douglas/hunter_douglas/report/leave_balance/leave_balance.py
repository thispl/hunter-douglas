# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext.hr.doctype.leave_application.leave_application \
import get_leave_allocation_records, get_leave_balance_on, get_approved_leaves_for_period, get_total_allocated_leaves

def execute(filters=None):
	leave_types = frappe.db.sql_list("select name from `tabLeave Type` order by name asc")
	leave_types_short = frappe.db.sql_list("select short_code from `tabLeave Type` order by name asc")
	columns = get_columns(leave_types)
	data = get_data(filters, leave_types)
	return columns, data

def get_columns(leave_types_short):
	columns = [
		_("Employee") + ":Link/Employee:60",
		_("Employee Name") + "::80",
		# _("Department") +"::50"
 	]
	for leave_types_short in leave_types_short:
		frappe.errprint(leave_types_short)
		if leave_types_short == 'Casual Leave':
			columns.append(_('CL') + " " + _("Opening") + ":Float:60")
			columns.append(_("CL") + " " + _("Taken") + ":Float:80")
			columns.append(_("CL") + " " + _("Balance") + ":Float:80")
		elif leave_types_short == 'Leave Without Pay':
			columns.append(_('LOP') + " " + _("Opening") + ":Float:80")
			columns.append(_("LOP") + " " + _("Taken") + ":Float:80")
			columns.append(_("LOP") + " " + _("Balance") + ":Float:80")
		elif leave_types_short == 'Privilege Leave':
			columns.append(_('PL') + " " + _("Opening") + ":Float:80")
			columns.append(_("PL") + " " + _("Taken") + ":Float:80")
			columns.append(_("PL") + " " + _("Balance") + ":Float:80")
		elif leave_types_short == 'Sick Leave':
			columns.append(_('SL') + " " + _("Opening") + ":Float:80")
			columns.append(_("SL") + " " + _("Taken") + ":Float:80")
			columns.append(_("SL") + " " + _("Balance") + ":Float:80")
	return columns

def get_data(filters, leave_types):
	user = frappe.session.user
	frappe.errprint(user)
	allocation_records_based_on_to_date = get_leave_allocation_records(filters.to_date)
	allocation_records_based_on_from_date = get_leave_allocation_records(filters.from_date)
	if user == 'Administrator':
		active_employees = frappe.get_all("Employee",filters = { "status": "Active" , "company": filters.company},fields = ["name", "employee_name"])
		data = []
		for employee in active_employees:		
			row = [employee.name, employee.employee_name]
			for leave_type in leave_types:
				# leaves taken
				leaves_taken = get_approved_leaves_for_period(employee.name, leave_type,
					filters.from_date, filters.to_date)
				
				# opening balance
				opening = get_total_allocated_leaves(employee.name, leave_type, filters.to_date)
				# closing bala
				closing = get_leave_balance_on(employee.name, leave_type, filters.to_date,
					allocation_records_based_on_to_date.get(employee.name, frappe._dict()))
				row += [opening, leaves_taken, closing]
			data.append(row)
	elif user == 'hr.hdi@hunterdouglas.asia':
		active_employees = frappe.get_all("Employee",filters = { "status": "Active" , "company": filters.company},fields = ["name", "employee_name"])
		data = []
		for employee in active_employees:		
			row = [employee.name, employee.employee_name]
			for leave_type in leave_types:
				# leaves taken
				leaves_taken = get_approved_leaves_for_period(employee.name, leave_type,
					filters.from_date, filters.to_date)
				# opening balance
				opening = get_total_allocated_leaves(employee.name, leave_type, filters.to_date)
				# closing bala
				closing = get_leave_balance_on(employee.name, leave_type, filters.to_date,
					allocation_records_based_on_to_date.get(employee.name, frappe._dict()))
				row += [opening, leaves_taken, closing]
			data.append(row)
	else:
		active_employees = frappe.get_all("Employee",filters = { "user_id": user , "company": filters.company},fields = ["name", "employee_name"])
		data = []
		for employee in active_employees:		
			row = [employee.name, employee.employee_name]
			for leave_type in leave_types:
				# leaves taken
				leaves_taken = get_approved_leaves_for_period(employee.name, leave_type,
					filters.from_date, filters.to_date)
				# opening balance
				opening = get_total_allocated_leaves(employee.name, leave_type, filters.to_date)
				# closing bala
				closing = get_leave_balance_on(employee.name, leave_type, filters.to_date,
					allocation_records_based_on_to_date.get(employee.name, frappe._dict()))
				row += [opening, leaves_taken, closing]
			data.append(row)
	return data