# -*- coding: utf-8 -*-
# Copyright (c) 2018, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from datetime import datetime,timedelta
from frappe import _
from frappe.utils import today,flt,add_days,date_diff,getdate

class LeaveApproverIdentityError(frappe.ValidationError): pass
class TravelManagement(Document):
	def on_submit(self):
		if self.status == "Applied":
			frappe.throw(_("Only Applications with status 'Approved' and 'Rejected' can be submitted"))

	def validate(self):
		self.validate_approver()	

	def validate_approver(self):
		employee = frappe.get_doc("Employee", self.employee)
		approvers = [l.leave_approver for l in employee.get("leave_approvers")]

		if len(approvers) and self.approver not in approvers:
			frappe.throw(_("Approver must be one of {0}")
				.format(comma_or(approvers)), InvalidApproverError)

		elif self.approver and not frappe.db.sql("""select name from `tabHas Role`
			where parent=%s and role='Leave Approver'""", self.approver):
			frappe.throw(_("{0} ({1}) must have role 'Approver'")\
				.format(get_fullname(self.approver), self.approver), InvalidApproverError)

		elif self.docstatus==0 and len(approvers) and self.approver != frappe.session.user:
			self.status = 'Applied'

		elif self.docstatus==1 and len(approvers) and self.approver != frappe.session.user:
			frappe.throw(_("Only the selected Approver can submit this Application"),
				LeaveApproverIdentityError)

@frappe.whitelist()
def travel_att_mark(doc,method):
    if doc.status == "Approved": 
	request_days = date_diff(doc.to_date, doc.from_date) +1
	for number in range(request_days):
		attendance_date = add_days(doc.from_date, number)
		skip_attendance = validate_if_attendance_not_applicable(doc.employee,attendance_date)
		if not skip_attendance:
			attendance = frappe.new_doc("Attendance")
			attendance.employee = doc.employee
			attendance.employee_name = doc.employee_name
			attendance.status = "Present"
			attendance.attendance_date = attendance_date
			# attendance.company = doc.company
			attendance.late_in = "00:00:00"
			attendance.work_time = "00:00:00"
			attendance.early_out = "00:00:00"
			attendance.overtime = "00:00:00"
			attendance.save(ignore_permissions=True)
			attendance.submit()

def validate_if_attendance_not_applicable(employee, attendance_date):
    # Check if attendance_date is a Holiday
	if is_holiday(employee, attendance_date):
		frappe.msgprint(_("Attendance not submitted for {0} as it is a Holiday.").format(attendance_date), alert=1)
		return True
    # Check if employee on Leave
	leave_record = frappe.db.sql("""select half_day from `tabLeave Application`
			where employee = %s and %s between from_date and to_date
			and docstatus = 1""", (employee, attendance_date), as_dict=True)
	if leave_record:
		frappe.msgprint(_("Attendance not submitted for {0} as {1} on leave.").format(attendance_date, employee), alert=1)
		return True

	return False

def get_holiday_list_for_employee(employee, raise_exception=True):
	if employee:
		holiday_list, company = frappe.db.get_value("Employee", employee, ["holiday_list", "company"])
	else:
		holiday_list=''
		company=frappe.db.get_value("Global Defaults", None, "default_company")

	if not holiday_list:
		holiday_list = frappe.get_cached_value('Company',  company,  "default_holiday_list")

	if not holiday_list and raise_exception:
		frappe.throw(_('Please set a default Holiday List for Employee {0} or Company {1}').format(employee, company))

	return holiday_list

def is_holiday(employee, date=None):
	'''Returns True if given Employee has an holiday on the given date
	:param employee: Employee `name`
	:param date: Date to check. Will check for today if None'''

	holiday_list = get_holiday_list_for_employee(employee)
	if not date:
		date = today()

	if holiday_list:
		return frappe.get_all('Holiday List', dict(name=holiday_list, holiday_date=date)) and True or False
