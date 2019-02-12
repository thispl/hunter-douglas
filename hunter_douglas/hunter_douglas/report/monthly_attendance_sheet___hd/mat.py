# Copyright (c) 2013, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import time
import math
from datetime import datetime,timedelta
from calendar import monthrange
from frappe.utils import getdate, cint, add_months, date_diff, add_days, nowdate, \
    get_datetime_str, cstr, get_datetime, time_diff, time_diff_in_seconds

def execute(filters=None):
    if not filters:
        filters = {}
    data = row = []
    att_late_in = att_overtime = ""
    filters["month"] = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
        "Dec"].index(filters.month) + 1  
    columns = [_("User ID") + ":Data:100",_("Name") + ":Data:100",_("Designation") + ":Data:100"] 
    
    month_f = filters.month - 1
    if month_f == 0:
        month_f = 12
        filters.year = cint(filters.year) - 1
    tdm = monthrange(cint(filters.year), month_f)[1]
    days = range(25,tdm+1) + range(1,25)
    for day in days:
        columns += [(_(day) + "::60") ]
    columns += [_("Total Present") + ":Float:80", _("Total Leaves") + ":Float:80",  _("Total Absent") + ":Float:80"]    
    for emp in get_employees(filters):
        row = [emp.employee,emp.employee_name,emp.designation]
        total_p = total_a = total_l = 0.0
        for day in days:           
            if day in range(25,32):
                day_f = str(filters.year) +'-'+str(month_f)+'-'+str(day)
            else:
                day_f = str(filters.year) +'-'+str(filters.month)+'-'+str(day) 
            att = frappe.db.get_value("Attendance",{ "employee":emp.employee,"attendance_date":day_f},['status'],as_dict=1)	
            holiday_list = frappe.db.get_value("Employee", {'employee':emp.employee},['holiday_list'])
            holiday_date = frappe.db.get_all("Holiday", filters={'holiday_date':day_f,'parent': holiday_list},fields=['name','is_ph'])
        
            leave_record = frappe.db.get_value("Leave Application", {'employee':emp.employee,'from_date':day_f,'to_date':day_f,"docstatus": 1},['name'])
            leave_type = frappe.db.get_value("Leave Application", {'name':leave_record},['leave_type1'])

            if att.in_time:
                dt = datetime.strptime(att.in_time, "%d/%m/%Y %H:%M:%S")
                from_time = dt.time()
                shift_in_time = frappe.db.get_value("Working Shift",working_shift,"in_time")
                emp_in_time = timedelta(hours=from_time.hour,minutes=from_time.minute,seconds=from_time.second)
                    #Check Movement Register
                if get_mr_in(att.employee,att.attendance_date):
                    emp_in_time = emp_in_time - get_mr_in(att.employee,att.attendance_date)

                if emp_in_time > shift_in_time:
                    late_in = emp_in_time - shift_in_time
                else:
                    late_in = timedelta(seconds=0)  

            if att.out_time:
                dt = datetime.strptime(att.out_time, "%d/%m/%Y %H:%M:%S")
                end_time = dt.time()
                shift_out_time = frappe.db.get_value("Working Shift",working_shift,"out_time")
                emp_out_time = timedelta(hours=end_time.hour,minutes=end_time.minute,seconds=end_time.second)
                #Check Movement Register
                if get_mr_out(att.employee,att.attendance_date):
                    emp_out_time = emp_out_time + get_mr_out(att.employee,att.attendance_date)

                if emp_out_time < shift_out_time:
                    early_out = shift_out_time - emp_out_time
                else:
                    early_out = timedelta(seconds=0)

            if holiday_date:
                for h in holiday_date:
                    if h['is_ph']:
                        row += ["PH"]
                    else:
                        row += ["WO"]  
            elif att:
                if att.status == 'Present':
                    status = 'P'
                    total_p += 1
                elif att.status == 'Half Day':    
                    status = 'HD'
                    total_p += 0.5
                    total_a += 0.5
                    total_l += 0.5
                elif att.status == 'Absent':
                    if leave_type:
                        total_l += 1
                        if leave_type == "Privilege Leave":
                            status = ["PL"]
                        elif leave_type == "Casual Leave":
                            status = ["CL"]
                        elif leave_type == "Sick Leave":
                            status = ["SL"]
                    else:
                        status = 'A'        
                        total_a += 1  
                if status:    
                    row += [status]
                else:
                    row +=[""]   
            else:
               row +=[""]          
        row += [total_p, total_l, total_a]      
        data.append(row)
    return columns, data
   
def get_attendance(filters):
    # att = frappe.db.sql(
    #     """select `tabAttendance`.employee,`tabAttendance`.employee_name,`tabAttendance`.working_shift,`tabAttendance`.attendance_date,`tabAttendance`.department,`tabAttendance`.designation  from `tabAttendance`  
    #     WHERE `tabAttendance`.status = "Present" group by `tabAttendance`.employee order by `tabAttendance`.employee""",as_dict = 1)
    att = frappe.db.sql(
        """select `tabAttendance`.employee,`tabAttendance`.employee_name,`tabAttendance`.attendance_date,`tabEmployee`.department,`tabEmployee`.designation,`tabEmployee`.working_shift  from `tabAttendance`  
        LEFT JOIN `tabEmployee` on `tabAttendance`.employee = `tabEmployee`.employee
        WHERE `tabAttendance`.status = "Present" group by `tabAttendance`.employee order by `tabAttendance`.employee""",as_dict = 1)
    return att

def get_employees(filters):
    conditions = get_conditions(filters)
    query = """SELECT 
         employee as employee,employee_name,designation,working_shift FROM `tabEmployee` WHERE status='Active' %s
        ORDER BY employee""" %conditions
    data = frappe.db.sql(query, as_dict=1)
    return data

def get_conditions(filters):
    conditions = ""

    if filters.get("employee"):
        conditions += "AND employee = '%s'" % filters["employee"]

    if filters.get("department"):
        conditions += " AND department = '%s'" % filters["department"]
                
    if filters.get("location"):
        conditions += " AND location_name = '%s'" % filters["location"]

    if filters.get("business_unit"):
        conditions += " AND business_unit = '%s'" % filters["business_unit"]
         
    return conditions