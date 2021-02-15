# Copyright (c) 2013, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import math
from calendar import monthrange
from datetime import datetime,timedelta,date
from dateutil.rrule import * 
from frappe.utils import today,getdate, cint, add_months, date_diff, add_days, nowdate, \
    get_datetime_str, cstr, get_datetime, time_diff, time_diff_in_seconds
from hunter_douglas.hunter_douglas.report.monthly_absenteesim.monthly_absenteesim import validate_if_attendance_not_applicable    
def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()
    mr_status_in = mr_status_out = False
    data = []
    row = []
    leave_type=from_date_session=to_date_session=""
    conditions, filters = get_conditions(filters)
    total = from_time = late_in = early_out = shift_in_time = dt = 0
    attendance = get_attendance(conditions,filters)
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")
    for att in attendance:
        if att:
            if att.name:row = [att.name]
            else:row = ["-"]

            if att.attendance_date:row += [att.attendance_date]
            else:row = ["-"]

            if att.employee:row += [att.employee]
            else:row += ["-"] 
            
            if att.employee_name:row += [att.employee_name]
            else:row += ["-"]

            working_shift = frappe.db.get_value("Employee", {'employee':att.employee},['working_shift']) 
            assigned_shift = frappe.db.sql("""select shift from `tabShift Assignment`
                        where employee = %s and %s between from_date and to_date""", (att.employee, att.attendance_date), as_dict=True)
            if assigned_shift:
                working_shift = assigned_shift[0]['shift']
            
            if working_shift:row += [working_shift]
            else:row += ["-"]

            holiday_list = frappe.db.get_value("Employee", {'employee':att.employee},['holiday_list'])

            holiday_date = frappe.db.get_all("Holiday", filters={'holiday_date':att.attendance_date,'parent': holiday_list},fields=['holiday_date','name','is_ph'])
            if att.in_time:
                dt = datetime.strptime(att.in_time, "%d/%m/%Y %H:%M:%S")
                from_time = dt.time()
                shift_in_time = frappe.db.get_value("Working Shift",working_shift,"in_time")
                emp_in_time = timedelta(hours=from_time.hour,minutes=from_time.minute,seconds=from_time.second)
                #Check Movement Register
                if get_mr_in(att.employee,att.attendance_date):
                    mr_status_in = True
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
                    mr_status_out = True
                    emp_out_time = emp_out_time + get_mr_out(att.employee,att.attendance_date)

                if emp_out_time < shift_out_time:
                    early_out = shift_out_time - emp_out_time
                else:
                    early_out = timedelta(seconds=0)   

            if holiday_date:
                for h in holiday_date:  
                    if get_continuous_absents(att.employee,att.attendance_date):    
                        # frappe.errprint(get_continuous_absents(att.employee,att.attendance_date))
                        row += ["AB","AB"]       
                    else:    
                        [att.first_half_status,att.second_half_status]        
            else:
                exc = frappe.db.get_list("Auto Present Employees",fields=['employee'])
                auto_present_list = []
                for e in exc:
                    auto_present_list.append(e.employee)
                
                if att.in_time and att.attendance_date == date.today():
                    row += ["In","-"]   
                elif att.employee in auto_present_list:
                    row += ["PR","PR"]      
                else:   
                    row += [att.first_half_status,att.second_half_status]    

            if att.in_time:               
                row += [from_time.isoformat()]
            else:row += ["-"]

            if att.out_time:   
                row += [end_time.isoformat()]
            else:row += ["-"]    
    
            if att.in_time and late_in:row += [late_in]
            else:row += ["-"]

            if att.out_time and early_out:row += [early_out]
            else:row += ["-"]

            if att.work_time:row += [att.work_time]
            else:row += ["-"]

            if att.overtime:row += [att.overtime]
            else:row += ["-"]    
        else:
            row += ["AB","AB"]

        data.append(row)

    return columns, data

def get_columns():
    columns = [
        _("Name") + ":Link/Attendance:100",
        _("Attendance Date") + ":Date:100",
        _("Employee") + ":Link/Employee:100", 
        _("Employee Name") + ":Data:180",
        _("Shift") + ":Link/Working Shift:90",
        _("Session1") + ":Data:90",
         _("Session2") + ":Data:90",
        _("In Time") + ":Data:90",
        _("Out Time") + ":Data:90",
        # _("Time Diff") + ":Data:90",
        _("Late In") + ":Data:90",
        # _("MR Status") + ":Data:90",
        _("Early Out") + ":Data:90",
        _("Work Time") + ":Data:90",
         _("Over Time") + ":Data:90",
    ]
    return columns

def get_attendance(conditions,filters):
    # exc = frappe.db.get_list("Auto Present Employees",fields=['employee'])
    # employees_list = []
    # for e in exc:
    #     employees_list.append(e.employee)
    # employees = frappe.get_all('Employee',{'status':'Active'})
    # for emp in employees:
    #     if emp.name not in employees_list:
    attendance = frappe.db.sql("""select att.admin_approved_status,att.late_in as late_in,att.early_out as early_out,att.first_half_status as first_half_status,att.second_half_status as second_half_status,att.name as name,att.employee_name as employee_name,att.attendance_date as attendance_date,att.work_time as work_time,att.overtime as overtime,att.employee as employee, att.employee_name as employee_name,att.status as status,att.in_time as in_time,att.out_time as out_time from `tabAttendance` att 
    where  docstatus = 1 %s order by att.attendance_date,att.employee""" % conditions, filters, as_dict=1)
    return attendance

def get_conditions(filters):
    conditions = ""
    if filters.get("from_date"): conditions += "and att.attendance_date >= %(from_date)s"
    if filters.get("to_date"): conditions += " and att.attendance_date <= %(to_date)s"  
    if filters.get("status_in"): conditions += " and att.in_time > 0"  
    if filters.get("employee"):conditions += "AND att.employee = '%s'" % filters["employee"]
    if filters.get("department"):conditions += " AND att.department = '%s'" % filters["department"]
    if filters.get("location"):conditions += " AND att.location = '%s'" % filters["location"]    

    if not frappe.get_doc("User", frappe.session.user).get("roles",{"role": "System Manager"}):   
        employee = frappe.db.get_value("Employee",{"user_id":filters.get("user")})
        if filters.get("user"): conditions += " and att.employee = %s" % employee
    return conditions, filters

            

def get_continuous_absents(emp,day):
    preday = postday = day
    while validate_if_attendance_not_applicable(emp,postday):
        postday = add_days(postday,1)
    # frappe.errprint(postday)    
    next_day = frappe.db.get_value("Attendance",{"attendance_date":postday,"employee":emp},["status"])
    next_day_admin_status = frappe.db.get_value("Attendance",{"attendance_date":postday,"employee":emp},["admin_approved_status"]) 
    while validate_if_attendance_not_applicable(emp,preday):
        preday = add_days(preday,-1)   
    # frappe.errprint(preday)      
    prev_day = frappe.db.get_value("Attendance",{"attendance_date":preday,"employee":emp},["status"])       
    prev_day_admin_status = frappe.db.get_value("Attendance",{"attendance_date":preday,"employee":emp},["admin_approved_status"])
    if prev_day == 'Absent' and next_day == 'Absent':
        frappe.errprint(prev_day)
        frappe.errprint(next_day)
        if next_day_admin_status == "WO" or prev_day_admin_status == "WO":
            return False
        else:
            return True
    return False    
    
def get_other_day(emp,day):
    holiday = False  
    if is_holiday(emp,day):
        holiday = True

    return holiday

# def get_next_day(emp,day):
#     holiday = False  
#     if is_holiday(emp,day):
#         holiday = True
#     return holiday            


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

def get_mr_out(emp,day):
    from_time = to_time = 0
    dt = datetime.combine(day, datetime.min.time())
    mrs = frappe.db.sql("""select from_time,to_time from `tabMovement Register` where employee= '%s' and docstatus=1 and status='Approved' and from_time between '%s' and '%s' """ % (emp,dt,add_days(dt,1)),as_dict=True)
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
    mrs = frappe.db.sql("""select from_time,to_time from `tabMovement Register` where employee= '%s' and docstatus=1 and status='Approved' and from_time between '%s' and '%s' """ % (emp,dt,add_days(dt,1)),as_dict=True)
    for mr in mrs:
        from_time = mr.from_time
        to_time = mr.to_time
    in_time = frappe.get_value("Attendance",{"employee":emp,"attendance_date":day},["in_time"])
    if in_time:    
        att_in_time = datetime.strptime(in_time,'%d/%m/%Y %H:%M:%S')
        if from_time:
            if att_in_time >= (from_time + timedelta(minutes=-10)):
                return to_time - from_time

@frappe.whitelist()
def get_filter_dates():
    from_date = rrule(MONTHLY, count=1, dtstart=add_months(date.today(),-1), bymonthday=25)[0]
    to_date = rrule(MONTHLY, count=1, dtstart=date.today(), bymonthday=24)[0]
    return from_date,to_date