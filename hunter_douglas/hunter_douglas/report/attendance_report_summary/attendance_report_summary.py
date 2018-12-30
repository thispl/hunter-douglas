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
    filters["month"] = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
        "Dec"].index(filters.month) + 1  
    columns = [_("User ID") + ":Data:100",_("Name") + ":Data:150",_("Designation") + ":Data:150",_("Total Present Days") + ":Data:100",_("Total Absent Days") + ":Data:150",_("Total Half Days") + ":Data:150",_("Total Leave Applications") + ":Data:100",_("Total On Duty Applications") + ":Data:100",_("Total Travel Management Applications") + ":Data:100",_("Total Movement Register Applications") + ":Data:100"] 
    tdm = monthrange(cint(filters.year), filters.month - 1)[1]
    days = range(25,tdm+1) + range(1,25)
    employees = get_employees(filters)
    for emp in get_employees(filters):     
        row = [emp.employee,emp.employee_name,emp.designation]   
        emp_status = [] 
        halfday_status = []
        leave_app =[]  
        for day in days:   
            if day in range(25,32):
                day_f = str(filters.year) +'-'+str(filters.month - 1)+'-'+str(day)
            else:
                day_f = str(filters.year) +'-'+str(filters.month)+'-'+str(day)  
            present = frappe.db.sql(
                    """select att.attendance_date from `tabAttendance` att where att.status = 'Present' and att.employee = '%s' and att.attendance_date='%s'""" % (emp.employee,day_f) ,as_dict=1)      
            row += [present]
            frappe.errprint(present)
            attend = frappe.db.sql(
                    """select att.status,att.attendance_date from `tabAttendance` att where att.status = 'Absent' and att.employee = '%s' and att.attendance_date='%s'""" % (emp.employee,day_f) ,as_dict=1)      
            if attend:
                for at in attend:
                    holiday_list = frappe.db.get_value("Employee", {'employee':emp.employee},['holiday_list'])
                    hd = frappe.db.get_all("Holiday", filters={'holiday_date':at.attendance_date,'parent': holiday_list},fields=['name','holiday_date'])
                    if not hd:
                        leave_record = frappe.db.get_value("Leave Application", {'employee':emp.employee,'from_date':at.attendance_date,'to_date':at.attendance_date,"docstatus": 1},['name'])
                        if not leave_record:
                            emp_status.append(at.attendance_date.strftime("%d"))
                        else:
                            leave_app.append(at.attendance_date.strftime("%d"))
            half_day_attendance = frappe.db.sql(
                    """select att.status,att.attendance_date from `tabAttendance` att where att.status = 'Half Day' and att.employee = '%s' and att.attendance_date='%s'""" % (emp.employee,day_f) ,as_dict=1)      
            if half_day_attendance:
                for hda in half_day_attendance:
                    holiday_list1 = frappe.db.get_value("Employee", {'employee':emp.employee},['holiday_list'])
                    hds = frappe.db.get_all("Holiday", filters={'holiday_date':at.attendance_date,'parent': holiday_list1},fields=['name','holiday_date'])
                    if not hds:
                        halfday_record = frappe.db.get_value("Leave Application", {'employee':emp.employee,'from_date':at.attendance_date,'to_date':at.attendance_date,"docstatus": 1},['name'])
                        if not halfday_record:
                            halfday_status.append(at.attendance_date.strftime("%d"))
                        else:
                            leave_app.append(at.attendance_date.strftime("%d"))
        ab = len(emp_status)
        row += [ab]
        h_total = len(halfday_status) 
        row += [h_total] 
        l_total = len(leave_app) 
        row += [l_total]    
        data.append(row)  
    return columns, data


def get_employees(filters):
    conditions = get_conditions(filters)
    query = """SELECT 
         employee as employee,employee_name,designation FROM `tabEmployee` WHERE status='Active' %s
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