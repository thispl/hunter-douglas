# Copyright (c) 2013, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from datetime import datetime
import time

def execute(filters=None):
    if not filters:
        filters = {}
    data = row = []
    in_time_row = []
    late_in_row = []
    early_out_row = []
    over_time_row = []
    work_time_row = []
    filters["month"] = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
        "Dec"].index(filters.month) + 1
    
    columns = [_("User ID") + ":Data:100",_("Name") + ":Data:100",_("Designation") + ":Data:100",_("Details") + ":Data:100"] 

    days = range(25,32) + range(1,25)
    for day in days:
        columns += [(_(day) + "::80") ]
    attendance = get_attendance(filters)
    for att in attendance:
        row = [att.employee,att.employee_name,att.designation,"Shift"]
        in_time_row = ["","","","In Time"]
        late_in_row = ["","","","Late IN"]
        early_out_row = ["","","","Early OUT"]
        over_time_row = ["","","","Over Time"]
        work_time_row = ["","","","Work Time"]
        for day in days:
            if day in range(25,32):
                day_f = str(filters.year) +'-'+str(filters.month - 1)+'-'+str(day)
            else:
                day_f = str(filters.year) +'-'+str(filters.month)+'-'+str(day) 
            # attend = frappe.get_list("Attendance",fields=['in_time','out_time','late_in','early_out','work_time','working_shift','overtime'],filters={'status':'Present','attendance_date':day_f})    
            attend = frappe.db.sql(
                    """select att.late_in,att.working_shift,att.in_time,att.early_out,att.overtime,att.work_time from `tabAttendance` att where att.status='Present' and 
                        att.attendance_date='%s'""" % (day_f) ,as_dict=1)    
            for at in attend:
                if at['working_shift']:
                    att_shift = at['working_shift']
                else:
                    att_shift = ""
                if at.in_time:
                    att_in_time = at.in_time
                else:
                    att_in_time = ""
                if at.late_in:
                    att_late_in = at.late_in
                else:
                    att_late_in = ""
                if at.early_out:
                    att_early_out = at.early_out
                else: 
                    att_early_out = ""
                if at.overtime:
                    att_overtime = at.overtime
                else:
                    at.overtime = ""
                if at.work_time:
                    att_work_time = at.work_time
                else:
                    att_work_time = ""
            row += [att_shift]
            in_time_row += [att_in_time]
            late_in_row += [att_late_in]
            early_out_row += [att_early_out]
            over_time_row += [att_overtime]
            work_time_row += [att_work_time]
        data.append(row)
        data.append(in_time_row)
        data.append(late_in_row)
        data.append(early_out_row) 
        data.append(over_time_row) 
        data.append(work_time_row)     
    return columns, data


def get_attendance(filters):
    # att = frappe.db.sql(
    #     """select `tabAttendance`.employee,`tabAttendance`.employee_name,`tabAttendance`.working_shift,`tabAttendance`.attendance_date,`tabAttendance`.department,`tabAttendance`.designation  from `tabAttendance`  
    #     WHERE `tabAttendance`.status = "Present" group by `tabAttendance`.employee order by `tabAttendance`.employee""",as_dict = 1)
    att = frappe.db.sql(
        """select `tabAttendance`.employee,`tabAttendance`.employee_name,`tabAttendance`.working_shift,`tabAttendance`.attendance_date,`tabEmployee`.department,`tabEmployee`.designation  from `tabAttendance`  
        LEFT JOIN `tabEmployee` on `tabAttendance`.employee = `tabEmployee`.employee
        WHERE `tabAttendance`.status = "Present" group by `tabAttendance`.employee order by `tabAttendance`.employee""",as_dict = 1)
    return att