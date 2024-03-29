# Copyright (c) 2013, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import math
from datetime import datetime,timedelta
from frappe.utils import getdate, cint, add_months, date_diff, add_days, nowdate, \
    get_datetime_str, cstr, get_datetime, time_diff, time_diff_in_seconds
def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()

    data = []
    row = []
    conditions, filters = get_conditions(filters)
    total = from_time = late_in = shift_in_time = 0
    attendance = get_attendance(conditions,filters)
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")
    for att in attendance:
        if att.name:row = [att.name]
        else:row = ["-"]

        if att.attendance_date:row += [att.attendance_date]
        else:row = ["-"]

        if att.employee:row += [att.employee]
        else:row += ["-"] 
        
        if att.employee_name:row += [att.employee_name]
        else:row += ["-"]

        if att.department:row += [att.department]
        else:row += ["-"]

        if att.business_unit:row += [att.business_unit]
        else:row += ["-"]

        if att.location:row += [att.location]
        else:row += ["-"]

        working_shift = frappe.db.get_value("Employee", {'employee':att.employee},['working_shift']) 
        if att.in_time:
            dt = datetime.strptime(att.in_time, '%Y-%m-%d %H:%M:%S')
            from_time = dt.time()
            shift_in_time = frappe.db.get_value("Working Shift",working_shift,"in_time")
            emp_in_time = timedelta(hours=from_time.hour,minutes=from_time.minute,seconds=from_time.second)
            if emp_in_time > shift_in_time:
                late_in = emp_in_time - shift_in_time
            else:
                late_in = ''    
            row += [from_time.isoformat()]
        else:row += ["-"]
        if att.out_time:
            dt = datetime.strptime(att.out_time,'%Y-%m-%d %H:%M:%S')
            end_time = dt.time()
            shift_out_time = frappe.db.get_value("Working Shift",working_shift,"out_time")
            emp_out_time = timedelta(hours=end_time.hour,minutes=end_time.minute,seconds=end_time.second)
            if emp_out_time < shift_out_time:
                early_out = shift_out_time - emp_out_time
            else:
                early_out = ''    
            row += [end_time.isoformat()]
        else:row += ["-"]
 
        if att.overtime :row += [att.overtime]
        else:row += ["-"]

        data.append(row)

    return columns, data

def get_columns():
    columns = [
        _("Name") + ":Link/Attendance:100",
        _("Attendance Date") + ":Date:100",
        _("Employee") + ":Link/Employee:100", 
        _("Employee Name") + ":Data:180",
        _("Department") + ":Data:90",
        _("Business Unit") + ":Data:90",
        _("Location") + ":Data:90",
        _("In Time") + ":Data:90",
        _("Out Time") + ":Data:90",
        _("Overtime") + ":Data:90",
    ]
    return columns

def get_attendance(conditions,filters):
    attendance = frappe.db.sql("""select att.overtime as overtime,att.status as status,att.location  as location, att.name as name,att.department as department,att.business_unit as business_unit,att.attendance_date as attendance_date,att.work_time as work_time,att.employee as employee, att.employee_name as employee_name,att.status as status,att.in_time as in_time,att.out_time as out_time from `tabAttendance` att 
    where att.status = "Present" %s order by att.attendance_date """ % conditions, filters, as_dict=1)
    return attendance

def get_conditions(filters):
    conditions = ""
    if filters.get("from_date"): conditions += "and att.attendance_date >= %(from_date)s"
    if filters.get("to_date"): conditions += " and att.attendance_date <= %(to_date)s"
    if filters.get("location"): conditions += " and att.location = %(location)s"  
    if filters.get("business_unit"): conditions += " and att.business_unit = %(business_unit)s"
   
    return conditions, filters