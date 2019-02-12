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
    in_time_row = []
    out_time_row = []
    late_in_row = []
    early_out_row = []
    over_time_row = []
    work_time_row = []
    first_session_row = []
    second_session_row = []
    att_late_in = att_overtime = ""
    filters["month"] = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
        "Dec"].index(filters.month) + 1  
    columns = [_("User ID") + ":Data:100",_("Name") + ":Data:100",_("Designation") + ":Data:100",_("Details") + ":Data:100"] 
    month = filters.month - 1
    if month == 0:
        month = 12
        filters.year = cint(filters.year) - 1
    tdm = monthrange(cint(filters.year), month)[1]
    days = range(25,tdm+1) + range(1,25)
    for day in days:
        columns += [(_(day) + "::80") ]
    for emp in get_employees(filters):
        row = [emp.employee,emp.employee_name,emp.designation,"Shift"]
        in_time_row = ["","","","In Time"]
        out_time_row = ["","","","Out Time"]
        late_in_row = ["","","","Late IN"]
        early_out_row = ["","","","Early OUT"]
        over_time_row = ["","","","Over Time"]
        work_time_row = ["","","","Work Time"] 
        first_session_row = ["","","","First Session"]
        second_session_row = ["","","","Second Session"]       
        for day in days:           
            if day in range(25,32):
                day_f = str(filters.year) +'-'+str(month)+'-'+str(day)
            else:
                day_f = str(filters.year) +'-'+str(filters.month)+'-'+str(day) 

            holiday_list = frappe.db.get_value("Employee", {'employee':emp.employee},['holiday_list'])
            holiday_date = frappe.db.get_list("Holiday", filters={'holiday_date':day_f,'parent': holiday_list}, fields=['holiday_date'])
            if holiday_date:
                row = [emp.employee,emp.employee_name,emp.designation,"Shift"]
                #row += ["WO"]
                in_time_row += ["WO"]
                out_time_row += ["WO"]
                late_in_row += ["WO"]
                early_out_row += ["WO"]
                over_time_row += ["WO"]
                work_time_row += ["WO"]
                first_session_row += ["WO"]
                second_session_row += ["WO"]
            else:
                attend = frappe.db.sql(
                        """select att.working_shift,att.in_time,att.out_time,att.early_out,att.overtime,att.work_time from `tabAttendance` att where att.employee = '%s' and att.attendance_date='%s'""" % (emp.employee,day_f) ,as_dict=1)      
                if attend:
                    for at in attend:
                        if at.working_shift:
                            att_shift = emp.working_shift
                            row += [emp.working_shift]
                        else:
                            att_shift = ""
                        if at.in_time:
                            att_in_time = at.in_time                   
                        else:
                            att_in_time = ""
                        if at.out_time:
                            att_out_time = at.out_time                   
                        else:
                            att_out_time = ""
                        if att_in_time:
                            in_time_f = datetime.strptime(att_in_time, "%d/%m/%Y %H:%M:%S")
                            from_time = in_time_f.time()
                            shift_in_time = frappe.db.get_value("Working Shift",emp.working_shift,"in_time")
                            emp_in_time = timedelta(hours=from_time.hour,minutes=from_time.minute,seconds=from_time.second)
                            if emp_in_time > shift_in_time:
                                att_late_in = emp_in_time - shift_in_time
                            else:
                                att_late_in = ""
                        else:
                            att_late_in = ""
                        if at.early_out:
                            att_early_out = at.early_out
                        else: 
                            att_early_out = ""
                        if at.overtime:
                            att_overtime = at.overtime
                        else:
                            att_overtime = ""
                        if at.work_time:
                            att_work_time = at.work_time
                        else:
                            att_work_time = ""
                        if att_in_time:
                            in_time_f = datetime.strptime(att_in_time, "%d/%m/%Y %H:%M:%S")
                            in_time_row += [in_time_f.time().isoformat()]
                        else:
                            in_time_row += ["-"]   
                        if att_out_time:
                            out_time_f = datetime.strptime(att_out_time, "%d/%m/%Y %H:%M:%S")
                            out_time_row += [out_time_f.time().isoformat()]
                        else:
                            out_time_row += ["-"]
                        if att_late_in:
                            late_in_row += [att_late_in]
                        else:
                            late_in_row += ["-"] 
                        if early_out_row:       
                            early_out_row += [att_early_out]
                        else:
                            early_out_row += ["-"]   
                        if att_overtime:
                            over_time_row += [att_overtime]
                        else:
                            over_time_row += ["-"]
                        if work_time_row:     
                            work_time_row += [att_work_time]
                        else:
                            work_time_row += ["-"] 
                        if first_session_row:     
                            first_session_row += [""]
                        else:
                            first_session_row += ["-"]  
                        if second_session_row:     
                            second_session_row += [emp.working_shift]
                        else:
                            second_session_row += ["-"]  
                        # else:
                        #     row += [emp.working_shift]
                        #     row += ["-"]
                        #     in_time_row += ["-"]
                        #     late_in_row += ["-"]
                        #     early_out_row += ["-"]
                        #     over_time_row += ["-"]
                        #     work_time_row += ["-"]     
        data.append(row)
        data.append(in_time_row)
        data.append(out_time_row)
        data.append(late_in_row)
        data.append(early_out_row) 
        data.append(over_time_row) 
        data.append(work_time_row)
        data.append(first_session_row) 
        data.append(second_session_row)     
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
        
    return conditions