# Copyright (c) 2013, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import time
import math
from datetime import datetime,timedelta,date
from calendar import monthrange
from frappe.utils import getdate, cint, add_months, date_diff, add_days, nowdate, \
    get_datetime_str, cstr, get_datetime, time_diff, time_diff_in_seconds
# from hunter_douglas.hunter_douglas.report.attendance_recapitulation.attendance_recapitulation import is_holiday
from hunter_douglas.hunter_douglas.report.monthly_absenteesim.monthly_absenteesim import validate_if_attendance_not_applicable    


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
    session1_row = []
    session2_row = []
    leave_day = 0
    total = from_time = late_in = early_out = shift_in_time = 0
    leave_type = ""
    att_late_in = att_overtime = ""
    filters["month"] = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
        "Dec"].index(filters.month) + 1  
    columns = [_("User ID") + ":Data:100",_("Name") + ":Data:100",_("Designation") + ":Data:100",_("Details") + ":Data:100"] 
    month = filters.month - 1
    year = filters.year
    if month == 0:
        month = 12
        year = cint(filters.year) - 1
    tdm = monthrange(cint(filters.year), month)[1]
    days = range(25,tdm+1) + range(1,25)
    for day in days:
        columns += [(_(day) + "::80") ]
    for emp in get_employees(filters):
        row = [emp.employee,emp.employee_name,emp.designation,"Shift"]
        working_shift = frappe.db.get_value("Employee", {'employee':emp.employee},['working_shift']) 
        in_time_row = ["","","","In Time"]
        out_time_row = ["","","","Out Time"]
        late_in_row = ["","","","Late IN"]
        early_out_row = ["","","","Early OUT"]
        over_time_row = ["","","","Over Time"]
        work_time_row = ["","","","Work Time"]
        session1_row = ["","","","Session1"]
        session2_row = ["","","","Session2"]     
        for day in days:           
            if day in range(25,32):
                day_f = str(year) +'-'+str(month)+'-'+str(day)
            else:
                day_f = str(filters.year) +'-'+str(filters.month)+'-'+str(day) 
            day_f = datetime.strptime(day_f, "%Y-%m-%d").date()
            holiday_list = frappe.db.get_value("Employee", {'employee':emp.employee},['holiday_list'])
            holiday_date = frappe.db.get_all("Holiday", filters={'holiday_date':day_f,'parent': holiday_list},fields=['holiday_date','name','is_ph'])
            # leave_record = get_leaves(emp.employee,day_f)
            att = frappe.get_value("Attendance",{"employee":emp.employee,"attendance_date":day_f},['admin_approved_status','name','attendance_date','status','late_in','early_out','first_half_status','second_half_status','employee','in_time','out_time','work_time','overtime'],as_dict=True)
            if att:
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
                
                if working_shift:row += [working_shift]
                else:row += ["-"]     

                if att.in_time:        
                    in_time_row += [from_time.isoformat()]
                else:  
                    in_time_row += ["-"]  

                if att.out_time:
                    out_time_row += [end_time.isoformat()]
                else:
                    out_time_row += ["-"]  

                if att.in_time and late_in:late_in_row += [late_in]
                else:late_in_row += ["-"]

                if att.out_time and early_out:early_out_row += [early_out]
                else:early_out_row += ["-"]

                if att.work_time:work_time_row += [att.work_time]
                else:work_time_row += ["-"]

                if att.overtime:over_time_row += [att.overtime]
                else:over_time_row += ["-"]  
                if att.admin_approved_status == 'Present':
                    session1_row += ["PR"]
                    session2_row += ["PR"]

                elif att.admin_approved_status == 'Absent':
                    session1_row += ["AB"]
                    session2_row += ["AB"]

                elif att.admin_approved_status == 'WO' or att.admin_approved_status == 'PH':
                    session1_row += [att.admin_approved_status]
                    session2_row += [att.admin_approved_status]

                elif holiday_date:
                    for h in holiday_date:
                        leave_record = get_leaves(att.employee,att.attendance_date)
                        tm_record = get_tm(att.employee,att.attendance_date)
                        od_record = get_od(att.employee,att.attendance_date)
                        if att.status == "On Duty":
                            status = 'OD'
                        elif get_continuous_absents(att.employee,att.attendance_date):
                            status = 'AB'
                        elif leave_record[0]:
                            session1_row += [leave_record[0]]
                            session2_row += [leave_record[0]]    
                        elif tm_record:
                            session1_row += ["TR"]
                            session2_row += ["TR"]
                        elif od_record[0]:
                            session1_row += ["OD"]
                            session2_row += ["OD"]    
                        else:    
                            if h['is_ph']:
                                status = 'PH'
                            else:
                                status = 'WO'
                    session1_row += [status]
                    session2_row += [status]
                elif att.status == "Absent":
                # Check if employee on Leave
                    leave_record = get_leaves(att.employee,att.attendance_date)
                    tm_record = get_tm(att.employee,att.attendance_date)
                    od_record = get_od(att.employee,att.attendance_date)
                    if leave_record[0]:
                        session1_row += [leave_record[0]]
                        session2_row += [leave_record[0]]
                    elif att.in_time and att.attendance_date == date.today():
                        session1_row += ["In"]
                        session2_row += ["AB"]
                    elif tm_record:
                        session1_row += ["TR"]
                        session2_row += ["TR"]
                    elif od_record[0]:
                        session1_row += ["OD"]
                        session2_row += ["OD"]
                    elif not att.in_time and not att.out_time:
                        session1_row += ["AB"]
                        session2_row += ["AB"]
                    else:   
                        session1_row += ["AB"]
                        session2_row += ["AB"]

                elif att.status == "On Leave":
                    leave_record = get_leaves(att.employee,att.attendance_date)
                    if leave_record:
                        session1_row += [leave_record[0]]
                        session2_row += [leave_record[0]]
                    else:    
                        session1_row += ["AB"]
                        session2_row += ["AB"]

                elif att.status == "Half Day":
                    leave_session = get_leaves(att.employee,att.attendance_date)
                    od_session = get_od(att.employee,att.attendance_date)
                    if leave_session[1]:
                        if leave_session[1] == "Second Half":
                            session1_row += ["PR"]
                            session2_row += [leave_session[0]]
                        elif leave_session[1] == "First Half":
                            session1_row += [leave_session[0]]
                            session2_row += ["PR"]
                        else: 
                            session1_row += [att.first_half_status]
                            session2_row += [att.second_half_status] 
                    elif od_session[1]:
                        if od_session[1] == "Second Half":
                            session1_row += ["PR"]
                            session2_row += [od_session[0]]
                        elif od_session[1] == "First Half":
                            session1_row += [od_session[0]]
                            session2_row += ["PR"] 
                        else:    
                            row += [att.first_half_status,att.second_half_status]          
                    else:
                        if late_in and late_in > timedelta(minutes=15) and early_out and early_out > timedelta(minutes=5):
                            session1_row += ["AB"]
                            session2_row += ["AB"]
                        elif late_in and late_in > timedelta(minutes=15):
                            session1_row += ["AB"]
                            session2_row += ["PR"]
                        elif early_out and early_out > timedelta(minutes=5):
                            session1_row += ["PR"]
                            session2_row += ["AB"]
                        else: 
                            session1_row += [att.first_half_status]
                            session2_row += [att.second_half_status]

                elif att.status == "On Duty":
                    session1_row += ["OD"]
                    session2_row += ["OD"]

                elif att.status == "Present":
                    if late_in and late_in > timedelta(minutes=15) and early_out and early_out > timedelta(minutes=5):
                        session1_row += ["AB"]
                        session2_row += ["AB"]
                    elif late_in and late_in > timedelta(minutes=15):
                        session1_row += ["AB"]
                        session2_row += ["PR"]
                    elif early_out and early_out > timedelta(minutes=5):
                        session1_row += ["PR"]
                        session2_row += ["AB"]
                    else:
                        tm_record = frappe.db.sql("""select half_day from `tabTour Application`
                            where employee = %s and %s between from_date and to_date
                            and docstatus = 1""", (att.employee, att.attendance_date), as_dict=True)
                        if tm_record:
                            session1_row += ["TR"]
                            session2_row += ["TR"]
                        else:
                            session1_row += ["PR"]
                            session2_row += ["PR"]
                # elif att.status == 'Present':
                #     if at.working_shift:
                #         att_shift = emp.working_shift
                #         row += [emp.working_shift]
                #     else:
                #         att_shift = ""    
                # else:
                #     att_shift = ""  
            columns += [(_("Total PR") + "::80"),(_("Total AB") + "::80") ] 
            session1_row += [session1_row.count("PR"),session1_row.count("AB")]   
            session2_row += [session2_row.count("PR"),session2_row.count("AB")]          
        data.append(row)
        data.append(in_time_row)
        data.append(out_time_row)
        data.append(late_in_row)
        data.append(early_out_row) 
        data.append(over_time_row) 
        data.append(work_time_row) 
        data.append(session1_row) 
        data.append(session2_row)  
          
    return columns, data
    
def get_attendance(filters):
    att = frappe.db.sql(
        """select `tabAttendance`.employee,`tabAttendance`.employee_name,`tabAttendance`.attendance_date,`tabEmployee`.department,`tabEmployee`.designation,`tabEmployee`.working_shift  from `tabAttendance`  
        LEFT JOIN `tabEmployee` on `tabAttendance`.employee = `tabEmployee`.employee
        WHERE `tabAttendance`.status = "Present" group by `tabAttendance`.employee order by `tabAttendance`.employee""",as_dict = 1)
    return att

def get_employees(filters):
    conditions = get_conditions(filters)
    query = """SELECT 
         employee as employee,employee_name,designation,working_shift FROM `tabEmployee` WHERE status='Active' %s
        ORDER BY employee""" % conditions
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

# def get_continuous_absents(emp,day):
#     prev_day = frappe.db.get_value("Attendance",{"attendance_date":add_days(day, -1),"employee":emp},["status"])
#     next_day = frappe.db.get_value("Attendance",{"attendance_date":add_days(day,1),"employee":emp},["status"])
#     current_day = frappe.db.get_value("Attendance",{"attendance_date":day,"employee":emp},["status"])
#     if prev_day == 'Absent' and next_day == 'Absent' and current_day == 'Absent':
#         return True
#     return False 

def get_continuous_absents(emp,day):
    preday = postday = day
    while validate_if_attendance_not_applicable(emp,postday):
        postday = add_days(postday,1)
    next_day = frappe.db.get_value("Attendance",{"attendance_date":postday,"employee":emp},["status"]) 
    while validate_if_attendance_not_applicable(emp,preday):
        preday = add_days(preday,-1)   
    prev_day = frappe.db.get_value("Attendance",{"attendance_date":preday,"employee":emp},["status"])       
    # frappe.errprint(preday)    
    if prev_day == 'Absent' and next_day == 'Absent':
        return True
    return False    
    
# def get_other_day(emp,day):
#     holiday = False  
#     if is_holiday(emp,day):
#         holiday = True
#     return holiday

def get_tm(emp,day):
    tm_record = frappe.db.sql("""select half_day from `tabTour Application`
                    where employee = %s and %s between from_date and to_date
                    and docstatus = 1""", (emp, day), as_dict=True) 
    if tm_record:
        return True
    return False

def get_leaves(emp,day):
    leave_type = from_date_session = to_date_session = leave = session = ""
    leave_record = frappe.db.sql("""select from_date,to_date,half_day,leave_type,from_date_session,to_date_session from `tabLeave Application`
                        where employee = %s and %s between from_date and to_date
                        and docstatus = 1""", (emp, day), as_dict=True)          
    if leave_record:
        for l in leave_record:
            leave_type = l.leave_type
            half_day = l.half_day
            from_date = l.from_date
            to_date = l.to_date
            from_date_session = l.from_date_session
            to_date_session = l.to_date_session
        if half_day:
            if from_date == to_date:
               session = from_date_session 
            else:   
                if from_date == day:
                    session = from_date_session
                elif to_date == day:
                    session = to_date_session  
        if leave_type == "Privilege Leave":
            leave = ["PL"]
        elif leave_type == "Casual Leave":
            leave = ["CL"]
        elif leave_type == "Sick Leave":
            leave = ["SL"]
        else:
            leave = ["LOP"]  
    return leave,session

def get_mr_out(emp,day):
    from_time = to_time = 0
    dt = datetime.combine(day, datetime.min.time())
    mrs = frappe.db.sql("""select from_time,to_time from `tabMovement Register` where employee= '%s' and from_time between '%s' and '%s' """ % (emp,dt,add_days(dt,1)),as_dict=True)
    for mr in mrs:
        from_time = mr.from_time
        to_time = mr.to_time
    out_time = frappe.get_value("Attendance",{"employee":emp,"attendance_date":day},["out_time"])  
    if out_time:
        att_out_time = datetime.strptime(out_time,'%d/%m/%Y %H:%M:%S')
        if from_time:
            if att_out_time >= (from_time + timedelta(minutes=-10)) :
                return to_time - from_time

def get_mr_in(emp,day):
    from_time = to_time = 0
    dt = datetime.combine(day, datetime.min.time())
    mrs = frappe.db.sql("""select from_time,to_time from `tabMovement Register` where employee= '%s' and from_time between '%s' and '%s' """ % (emp,dt,add_days(dt,1)),as_dict=True)
    for mr in mrs:
        from_time = mr.from_time
        to_time = mr.to_time
    in_time = frappe.get_value("Attendance",{"employee":emp,"attendance_date":day},["in_time"])
    if in_time:    
        att_in_time = datetime.strptime(in_time,'%d/%m/%Y %H:%M:%S')
        if from_time:
            if att_in_time >= (from_time + timedelta(minutes=-10)):
                return to_time - from_time

def get_od(emp,day):
    from_date_session = to_date_session = od = session = ""
    od_record = frappe.db.sql("""select from_date,to_date,half_day,from_date_session,to_date_session from `tabOn Duty Application`
                        where employee = %s and %s between from_date and to_date
                        and docstatus = 1""", (emp, day), as_dict=True)
    if od_record:
        for o in od_record:
            half_day = o.half_day
            from_date = o.from_date
            to_date = o.to_date
            from_date_session = o.from_date_session
            to_date_session = o.to_date_session
        if half_day:
            if from_date == to_date:
               session = from_date_session 
            else:   
                if from_date == day:
                    session = from_date_session
                elif to_date == day:
                    session = to_date_session  
        od = ["OD"]  
    return od,session

def get_tm(emp,day):
    tm_record = frappe.db.sql("""select half_day from `tabTour Application`
                    where employee = %s and %s between from_date and to_date
                    and docstatus = 1""", (emp, day), as_dict=True) 
    if tm_record:
        return True
    return False  