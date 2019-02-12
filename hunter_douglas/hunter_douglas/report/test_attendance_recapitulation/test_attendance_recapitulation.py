# Copyright (c) 2013, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _


def execute(filters=None):
    columns, data = [], []
    employees = frappe.get_all("Employee",{"status":"Active"})
    for emp in employees:
        row = [frappe.get_value("Employee",emp.name,"employee_name")]
        attendance = get_attendance(filters,emp.name)
        row += [attendance]
        # row += []

        data.append(row)  
    columns += [
        _("Name") + ":Link/Employee:100",
        _("Attendance Date") + ":Data:100"
        ]
    return columns, data

def get_attendance(filters,emp):
    att = frappe.db.sql("""select attendance_date from `tabAttendance` where employee ='%s' and attendance_date between '%s' and '%s'""" % (emp,filters.from_date,filters.to_date),as_dict=1)
    frappe.errprint(att)
    at_date = []
    for at in att:
        at_date.append(at.attendance_date)
    return at_date
