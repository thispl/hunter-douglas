# -*- coding: utf-8 -*-
# Copyright (c) 2017, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe,os,base64
import requests
import datetime
import json,calendar
from datetime import datetime,timedelta,date,time
import datetime as dt
from frappe.utils import cint,today,flt,date_diff,add_days,add_months,date_diff,getdate,formatdate,cint,cstr
from frappe.desk.notifications import delete_notification_count_for
from frappe import _
import xml.etree.ElementTree as ET
from hunter_douglas.doctype.on_duty_application.on_duty_application import validate_if_attendance_not_applicable
from frappe.email.email_body import (replace_filename_with_cid,
    get_email, inline_style_in_html, get_header)


@frappe.whitelist()
def fetch_revised():
    days = ["2019-03-25","2019-03-26","2019-03-27","2019-03-28","2019-03-29","2019-03-30","2019-03-31",
    "2019-04-01","2019-04-02","2019-04-03","2019-04-04","2019-04-05","2019-04-06","2019-04-07","2019-04-08","2019-04-09","2019-04-10","2019-04-11","2019-04-12","2019-04-13","2019-04-14","2019-04-15","2019-04-16","2019-04-17",
    "2019-04-18","2019-04-19","2019-04-20","2019-04-21","2019-04-22","2019-04-23","2019-04-24"]
    for day in days:
    # preday = datetime.strptime(today(), '%Y-%m-%d')
        preday = datetime.strptime(day, '%Y-%m-%d')
        day = preday.strftime("%d%m%Y")

        exc = frappe.db.get_list("Auto Present Employees",fields=['employee'])
        
        auto_present_list = []
        for e in exc:
            auto_present_list.append(e.employee)
        employees = frappe.get_all('Employee',{'status':'Active'})
        for emp in employees:
            if emp.name == "2031":
                working_shift = frappe.db.get_value("Employee", {'employee':emp.name},['working_shift']) 
                assigned_shift = frappe.db.sql("""select shift from `tabShift Assignment`
                            where employee = %s and %s between from_date and to_date""", (emp.name, preday), as_dict=True)
                if assigned_shift:
                    working_shift = assigned_shift[0]['shift']
                if emp.name in auto_present_list:
                    doc = frappe.get_doc("Employee",emp.name)
                    attendance = frappe.db.exists("Attendance", {"employee": doc.employee, "attendance_date": preday})
                    if attendance:
                        frappe.db.set_value("Attendance",attendance,"status","Absent")
                        frappe.db.commit()
                    else:
                        attendance = frappe.new_doc("Attendance")
                        attendance.employee = doc.employee
                        attendance.employee_name = doc.employee_name
                        attendance.status = "Absent"
                        attendance.attendance_date = preday
                        # attendance.company = doc.company
                        attendance.working_shift = working_shift
                        attendance.late_in = "00:00:00"
                        attendance.work_time = "00:00:00"
                        attendance.early_out = "00:00:00"
                        attendance.overtime = "00:00:00"
                        attendance.save(ignore_permissions=True)
                        attendance.submit()
                        frappe.db.commit()
                else:
                    url = 'http://182.72.89.102/cosec/api.svc/v2/attendance-daily?action=get;field-name=userid,ProcessDate,firsthalf,\
                            secondhalf,punch1,punch2,workingshift,shiftstart,shiftend,latein,earlyout,worktime,overtime;date-range=%s-%s;range=user;id=%s;format=xml' % (day,day,emp.name) 
                    r = requests.get(url, auth=('sa', 'matrixx'))
                    if "No records found" in r.content:
                        in_time = ""
                        out_time = ""
                        date = preday
                        date_f = date.strftime("%Y-%m-%d")
                        status = ""
                        work_time = "00:00:00" 
                        nd = get_att_data(emp.name,date_f,working_shift,in_time,out_time,status)
                        first_half_status = nd.first_half_status
                        second_half_status = nd.second_half_status
                        status = nd.status
                        late_in = nd.late_in
                        early_out = nd.early_out
                        work_time = timedelta(minutes=cint(nd.work_time))
                        over_time = timedelta(minutes=cint(nd.over_time))
                        attendance_id = frappe.db.exists("Attendance", {
                                "employee": emp.name, "attendance_date": preday,"docstatus":1})
                        if attendance_id:
                            attendance = frappe.get_doc(
                                "Attendance", attendance_id)
                            attendance.out_time = out_time
                            attendance.in_time = in_time
                            attendance.status = status 
                            attendance.first_half_status = first_half_status
                            attendance.second_half_status = second_half_status
                            attendance.late_in = late_in
                            attendance.early_out = early_out
                            attendance.working_shift = working_shift
                            attendance.work_time = work_time
                            attendance.overtime = over_time
                            attendance.db_update()
                            frappe.db.commit()
                        else:
                            attendance = frappe.new_doc("Attendance")
                            attendance.update({
                                "employee": emp.name,
                                "attendance_date": date_f,
                                "status": status,
                                "in_time": in_time,
                                "late_in" : late_in,
                                "early_out" : early_out,
                                "working_shift" : working_shift,
                                "out_time": out_time,
                                "work_time": work_time,
                                "overtime":over_time,
                                "first_half_status": first_half_status,
                                "second_half_status":second_half_status
                            })
                            attendance.save(ignore_permissions=True)
                            attendance.submit()
                            frappe.db.commit() 
                    else:    
                        if not "failed: 0010102003" in r.content:
                            root = ET.fromstring(r.content)
                            for att in root.findall('attendance-daily'):
                                userid = att.find('UserID').text
                                in_time = att.find('Punch1').text
                                out_time = att.find('Punch2').text
                                date = datetime.strptime((att.find('ProcessDate').text.replace("/","")), "%d%m%Y").date()
                                date_f = date.strftime("%Y-%m-%d")
                                status = ""
                                if flt(att.find('WorkTime').text) > 1440:
                                        work_time = timedelta(minutes=flt('1400'))
                                else:
                                    work_time = timedelta(minutes=flt(att.find('WorkTime').text)) 
                                nd = get_att_data(emp.name,date_f,working_shift,in_time,out_time,status)
                                first_half_status = nd.first_half_status
                                second_half_status = nd.second_half_status
                                status = nd.status
                                late_in = nd.late_in
                                early_out = nd.early_out
                                work_time = timedelta(minutes=cint(nd.work_time))
                                over_time = timedelta(minutes=cint(nd.over_time))
                              
                                # if status = ""
                                # if work_time >= timedelta(hours=4):
                                #     if work_time < timedelta(hours=7,minutes=45):
                                #         status = 'Half Day'
                                #     else:    
                                #         status = 'Present'
                                # else:
                                #     status = 'Absent'  
                                attendance_id = frappe.db.exists("Attendance", {
                                    "employee": emp.name, "attendance_date": date_f,"docstatus":1})       
                                if attendance_id:
                                    attendance = frappe.get_doc(
                                        "Attendance", attendance_id)
                                    attendance.out_time = out_time
                                    attendance.in_time = in_time
                                    attendance.status = status 
                                    attendance.first_half_status = first_half_status
                                    attendance.second_half_status = second_half_status
                                    attendance.late_in = late_in
                                    attendance.early_out = early_out
                                    attendance.working_shift = working_shift
                                    attendance.work_time = work_time
                                    attendance.overtime = over_time
                                    attendance.db_update()
                                    frappe.db.commit()
                                else:
                                    attendance = frappe.new_doc("Attendance")
                                    attendance.update({
                                        "employee": emp.name,
                                        "attendance_date": date_f,
                                        "status": status,
                                        "in_time": in_time,
                                        "late_in" : late_in,
                                        "early_out" : early_out,
                                        "working_shift" : working_shift,
                                        "out_time": out_time,
                                        "work_time": work_time,
                                        "overtime":over_time,
                                        "first_half_status": first_half_status,
                                        "second_half_status":second_half_status
                                    })
                                    attendance.save(ignore_permissions=True)
                                    attendance.submit()
                                    frappe.db.commit()

# @frappe.whitelist()	
# def duplicate():
#     employee = "1280"
#     attendance_date = "2019-02-23"
#     working_shift = "GF2"
#     in_time = "23/02/2019 08:54:50"
#     out_time = "23/02/2019 15:37:30"
#     d = get_att_data(employee,attendance_date,working_shift,in_time,out_time)



def get_att_data(employee,attendance_date,working_shift,in_time,out_time,status):
    first_half_status = second_half_status = 'AB'
    from_time = late_in = early_out = shift_in_time = shift_out_time = emp_in_time = dt = 0
    # working_shift = frappe.db.get_value("Employee",employee,"working_shift")
    shift_in_time = frappe.db.get_value("Working Shift",working_shift,"in_time")
    shift_out_time = frappe.db.get_value("Working Shift",working_shift,"out_time")  
    grace_in_time = frappe.db.get_value("Working Shift",working_shift,"grace_in_time")   
    grace_out_time = frappe.db.get_value("Working Shift",working_shift,"grace_out_time")   
    work_time = over_time = ""
    shift_in_time += grace_in_time
    shift_out_time -= grace_out_time
    if in_time:
        dt = datetime.strptime(in_time, "%d/%m/%Y %H:%M:%S")
        from_time = dt.time()       
        emp_in_time = timedelta(hours=from_time.hour,minutes=from_time.minute,seconds=from_time.second)
        #Check Movement Register
        if get_mr_in(employee,attendance_date):
            mr_status_in = True
            emp_in_time = emp_in_time - get_mr_in(employee,attendance_date)
        if emp_in_time > shift_in_time:
            first_half_status = 'AB'
            if second_half_status == "AB":
                status = "Absent"
            elif second_half_status == "PR":                   
                status = "Half Day"
            late_in = emp_in_time - shift_in_time
        else:
            first_half_status = 'PR'
            if second_half_status == "AB":
                status = "Half Day"
            elif second_half_status == "PR":                   
                status = "Present"
            late_in = timedelta(seconds=0)

    if out_time:
        if in_time:
            dt = datetime.strptime(out_time, "%d/%m/%Y %H:%M:%S")
            end_time = dt.time()
            emp_out_time = timedelta(hours=end_time.hour,minutes=end_time.minute,seconds=end_time.second)
            #Check Movement Register
            if get_mr_out(employee,attendance_date):
                mr_status_out = True
                emp_out_time = emp_out_time + get_mr_out(employee,attendance_date)
            if emp_out_time < shift_out_time:
                second_half_status = 'AB'
                if first_half_status == "AB":
                    status = "Absent"
                elif first_half_status == "PR":
                    status = "Half Day"
                early_out = shift_out_time - emp_out_time
            else:
                second_half_status = 'PR'
                if first_half_status == "AB":
                    status = "Half Day"
                elif first_half_status == "PR":
                    status = "Present"
                early_out = timedelta(seconds=0)  
    if in_time and out_time:
        out_time_f = datetime.strptime(out_time, "%d/%m/%Y %H:%M:%S")
        in_time_f = datetime.strptime(in_time, "%d/%m/%Y %H:%M:%S")
        work_time = (out_time_f - in_time_f).total_seconds() // 60
        if work_time > 1440:
            work_time = timedelta(minutes=flt('1400')) 
        if emp_out_time > shift_out_time:
            over_time = (emp_out_time - shift_out_time).total_seconds() // 60
            if over_time > 1440:
                over_time = timedelta(minutes=flt('1400')) 
    if not in_time and not out_time:
        first_half_status = second_half_status = "AB"
        status = "Absent"
        work_time = over_time = timedelta(minutes=0)
    attendance_id = frappe.db.exists("Attendance", {
                            "employee": employee, "attendance_date": attendance_date,"docstatus":1})       
    admin_status = ""
    if attendance_id:
        attendance = frappe.get_doc(
            "Attendance", attendance_id)
        admin_status = attendance.admin_approved_status
    if first_half_status == "AB" and second_half_status == "AB":
        other_details = get_details(employee,attendance_date,first_half_status,second_half_status,status)
        if other_details:
            first_half_status = other_details.first_half_status
            second_half_status = other_details.second_half_status
            status = other_details.status
    if first_half_status == "AB" and second_half_status == "PR":
        other_details = get_details(employee,attendance_date,first_half_status,second_half_status,status)
        if other_details:
            first_half_status = other_details.first_half_status
            status = other_details.status
    if first_half_status == "PR" and second_half_status == "AB":
        other_details = get_details(employee,attendance_date,first_half_status,second_half_status,status)
        if other_details:
            second_half_status = other_details.second_half_status
            status = other_details.status  
    if admin_status:
        if admin_status == "Present":
            first_half_status = "PR"
            second_half_status = "PR"
            status = "Present"
        if admin_status == "Absent":
            first_half_status = "AB"
            second_half_status = "AB"
            status = "Absent"
        if admin_status == "First Half Present":
            first_half_status = "PR"
            if second_half_status == "AB":
                status = "Half Day"
            else:                   
                status = "Present"
        if admin_status == "Second Half Present":
            second_half_status = "PR"
            if first_half_status == "AB":
                status = "Half Day"
            else:
                status = "Present"
        if admin_status == "First Half Absent":
            first_half_status = "AB"
            if second_half_status == "AB":
                status = "Absent"
            else:                   
                status = "Half Day"
        if admin_status == "Second Half Absent":
            second_half_status = "AB"
            if first_half_status == "AB":
                status = "Absent"
            else:
                status = "Half Day"
        if admin_status == "WO" or admin_status == "PH":
            first_half_status = admin_status
            second_half_status = admin_status
            status = "Absent"
    data = frappe._dict({
            "first_half_status": first_half_status,
            "second_half_status": second_half_status,
            "late_in": late_in,
            "early_out": early_out,
            "work_time": work_time,
            "over_time": over_time,
            "status": status
    })
    return data


def get_mr_out(emp,day):
    from_time = to_time = 0
    day = (datetime.strptime(str(day), '%Y-%m-%d')).date()
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
    day = (datetime.strptime(str(day), '%Y-%m-%d')).date()
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
def get_details(employee,attendance_date,first_half_status,second_half_status,status):
    if is_holiday(employee, attendance_date):
        holiday_type = is_holiday(employee, attendance_date)
        if holiday_type:
            for hl in holiday_type:
                if hl.is_ph == 0:
                    new_data = frappe._dict({
                        "first_half_status":"WO",
                        "second_half_status": "WO",
                        "status": "Absent"
                    })
                    return new_data
                else:
                    new_data = frappe._dict({
                        "first_half_status":"PH",
                        "second_half_status": "PH",
                        "status": "Absent"
                    })
                    return new_data
    # Check if employee on Leave
    ua = ""
    leave_record = frappe.db.sql("""select from_date,leave_type1,to_date,from_date_session,to_date_session from `tabLeave Application`
            where employee = %s and %s between from_date and to_date
            and docstatus = 1 and status='Approved'""", (employee, attendance_date), as_dict=True)
    if leave_record:
        for l in leave_record:
            m_status= ""
            if l.leave_type1 == "Casual Leave":
                m_status = "CL"
            if l.leave_type1 == "Privilege Leave":
                m_status = "PL"
            if l.leave_type1 == "Sick Leave":
                m_status = "SL"
            ua = update_attendance(employee,attendance_date,l.from_date,l.to_date,l.from_date_session,l.to_date_session,m_status,first_half_status,second_half_status,status)
    #Check if employee on On-Duty
    od_record = frappe.db.sql("""select from_date,to_date,from_date_session,to_date_session from `tabOn Duty Application`
            where employee = %s and %s between from_date and to_date
            and docstatus = 1 and status='Approved'""", (employee, attendance_date), as_dict=True)
    if od_record:
        for od in od_record:
            m_status = "OD"
            ua = update_attendance(employee,attendance_date,od.from_date,od.to_date,od.from_date_session,od.to_date_session,m_status,first_half_status,second_half_status,status) 
            
    # Check if employee on C-Off
    coff_record = frappe.db.sql("""select from_date,to_date,from_date_session,to_date_session from `tabCompensatory Off Application`
            where employee = %s and %s between from_date and to_date
            and docstatus = 1 and status='Approved'""", (employee, attendance_date), as_dict=True)
    if coff_record:
        for cr in coff_record:
            m_status = "Coff"
            ua = update_attendance(employee,attendance_date,cr.from_date,cr.to_date,cr.from_date_session,cr.to_date_session,m_status,first_half_status,second_half_status,status)  
    # Check if employee on Tour Management
    tm_record = frappe.db.sql("""select from_date,to_date,from_date_session,to_date_session from `tabTour Application`
                    where employee = %s and %s between from_date and to_date
                    and docstatus = 1 and status='Approved'""", (employee, attendance_date), as_dict=True) 
    if tm_record:
        for tm in tm_record:
            m_status = "TR"
            ua = update_attendance(employee,attendance_date,tm.from_date,tm.to_date,tm.from_date_session,tm.to_date_session,m_status,first_half_status,second_half_status,status)
    return ua


@frappe.whitelist()	
def is_holiday(employee, date=None):
    '''Returns True if given Employee has an holiday on the given date
    :param employee: Employee `name`
    :param date: Date to check. Will check for today if None'''
    holiday_list = get_holiday_list_for_employee(employee)
    if not date:
        date = today()

    if holiday_list:
        hl = frappe.get_all('Holiday', dict(parent=holiday_list, holiday_date=date),["is_ph"])
        return hl
        



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

@frappe.whitelist()
def update_attendance(employee,attendance_date,from_date,to_date,from_date_session,to_date_session,m_status,first_half_status,second_half_status,status):
    query = """select name from `tabAttendance` where employee=%s and attendance_date between '%s' and '%s' """ % (employee,from_date,to_date)
    attendance = frappe.db.sql(query,as_dict=True)
    from_date = (datetime.strptime(str(from_date), '%Y-%m-%d')).date()
    to_date = (datetime.strptime(str(to_date), '%Y-%m-%d')).date()
    attendance_date = (datetime.strptime(str(attendance_date), '%Y-%m-%d')).date()
    for a in attendance:
        if from_date == to_date:
            if from_date_session == "First Half":
                first_half_status = m_status,
                if second_half_status == "AB":
                    status = "Half Day"
                elif second_half_status == "PR":                   
                    status = "Present"
            elif from_date_session == "Second Half":
                second_half_status = m_status
                if first_half_status == "AB":
                    status = "Half Day"
                elif first_half_status == "PR":
                    status = "Present"              
            else:
                first_half_status = second_half_status = m_status
                if m_status != "CL" and m_status != "PL" and m_status != "SL":
                    status = "Present"
                else:
                    status = "On Leave"
        else:
            if attendance_date == from_date:
                if from_date_session == "Second Half":
                    second_half_status = m_status
                    if first_half_status == "AB":
                        status = "Half Day"
                    elif first_half_status == "PR":
                        status = "Present"
                elif from_date_session == "Full Day":
                    first_half_status = second_half_status = m_status,
                    if m_status != "CL" and m_status != "PL" and m_status != "SL":
                        status = "Present"
                    else:
                        status = "On Leave"
            elif attendance_date == to_date:
                if to_date_session == "First Half":
                    first_half_status = m_status,
                    if second_half_status == "AB":
                        status = "Half Day"
                    elif second_half_status == "PR":                   
                        status = "Present"
                elif to_date_session == "Full Day":
                    first_half_status = second_half_status = m_status,
                    if m_status != "CL" and m_status != "PL" and m_status != "SL":
                        status = "Present"
                    else:
                        status = "On Leave"
            else:
                first_half_status = second_half_status = m_status
                if m_status != "CL" and m_status != "PL" and m_status != "SL":
                    status = "Present"
                else:
                    status = "On Leave"
        new_data = frappe._dict({
            "first_half_status":first_half_status,
            "second_half_status": second_half_status,
            "status": status
        })
        return new_data


def update_attendance_by_app(employee,from_date,to_date,from_date_session,to_date_session,m_status):
    query = """select name from `tabAttendance` where employee=%s and attendance_date between '%s' and '%s' """ % (employee,from_date,to_date)
    attendance = frappe.db.sql(query,as_dict=True)
    from_date = (datetime.strptime(str(from_date), '%Y-%m-%d')).date()
    to_date = (datetime.strptime(str(to_date), '%Y-%m-%d')).date()
    for a in attendance:
        doc = frappe.get_doc("Attendance",a.name)
        attendance_date = (datetime.strptime(str(doc.attendance_date), '%Y-%m-%d')).date()
        first_half_status = doc.first_half_status
        second_half_status = doc.second_half_status
        status = doc.status
        if from_date == to_date:
            if from_date_session == "First Half":
                first_half_status = m_status,
                if second_half_status == "AB":
                    status = "Half Day"
                elif second_half_status == "PR":                   
                    status = "Present"
            elif from_date_session == "Second Half":
                second_half_status = m_status
                if first_half_status == "AB":
                    status = "Half Day"
                elif first_half_status == "PR":
                    status = "Present"              
            else:
                first_half_status = second_half_status = m_status
                if m_status != "CL" and m_status != "PL" and m_status != "SL":
                    status = "Present"
                else:
                    status = "On Leave"
        else:
            if attendance_date == from_date:
                if from_date_session == "Second Half":
                    second_half_status = m_status
                    if first_half_status == "AB":
                        status = "Half Day"
                    elif first_half_status == "PR":
                        status = "Present"
                elif from_date_session == "Full Day":
                    first_half_status = second_half_status = m_status,
                    if m_status != "CL" and m_status != "PL" and m_status != "SL":
                        status = "Present"
                    else:
                        status = "On Leave"
            elif attendance_date == to_date:
                if to_date_session == "First Half":
                    first_half_status = m_status,
                    if second_half_status == "AB":
                        status = "Half Day"
                    elif second_half_status == "PR":                   
                        status = "Present"
                elif to_date_session == "Full Day":
                    first_half_status = second_half_status = m_status,
                    if m_status != "CL" and m_status != "PL" and m_status != "SL":
                        status = "Present"
                    else:
                        status = "On Leave"
            else:
                first_half_status = second_half_status = m_status
                if m_status != "CL" and m_status != "PL" and m_status != "SL":
                    status = "Present"
                else:
                    status = "On Leave"
        doc.update({
            "first_half_status": first_half_status,
            "second_half_status": second_half_status,
            "status": status
        })
        doc.save(ignore_permissions=True)
        doc.submit()
        frappe.db.commit()





@frappe.whitelist()
def check_other_docs(employee,from_date,to_date,from_date_session,to_date_session):
    status = ""
    if from_date == to_date:
        doc_date = from_date
        session = from_date_session
        status = verify_other_docs(employee,doc_date,session)
    else:
        diff = date_diff(to_date,from_date)
        i = 0
        for i in range(diff):
            if i <= diff:
                if i == 0:
                    doc_date = from_date
                    session = from_date_session
                    status = verify_other_docs(employee,doc_date,session)
                    
                elif i == diff:
                    doc_date = to_date
                    session = to_date_session
                    status = verify_other_docs(employee,doc_date,session)
                else:
                    doc_date = add_days(from_date,i)
                    session = "Full Day"
                    status = verify_other_docs(employee,doc_date,session)
    if status != False:
        data = frappe._dict({
                "type":status[0],
                "date": status[1]
            })
        return data
    else:
        return "0"
        


@frappe.whitelist()
def verify_other_docs(employee,doc_date,session):
    doc_date = datetime.strptime(doc_date, '%Y-%m-%d').date()
    leave_record = frappe.db.sql("""select from_date,leave_type1,to_date,from_date_session,to_date_session from `tabLeave Application`
            where docstatus= 1 and employee = %s and %s between from_date and to_date """, (employee, doc_date), as_dict=True)
    if leave_record:
        if session == "Full Day":
            return "Leave",doc_date
        else:
            for l in leave_record:
                if l.from_date == l.to_date:
                    if l.from_date_session == session:
                        return "Leave",doc_date
                    else: 
                        return False
                else:
                    if l.from_date == doc_date:
                        if l.from_date_session == "Full Day" or l.from_date_session == session:
                            return "Leave",doc_date
                    elif l.to_date == doc_date and (l.to_date_session == "Full Day" or l.to_date_session == session):
                        return "Leave",doc_date
                    elif l.to_date > doc_date and l.from_date < doc_date:
                        return "Leave",doc_date
                    else:
                        return False
    else:
        # Check if employee on Tour Management
        tm_record = frappe.db.sql("""select from_date,to_date,from_date_session,to_date_session from `tabTour Application`
                        where employee = %s and %s between from_date and to_date """, (employee, doc_date), as_dict=True) 
        if tm_record:  
            if session == "Full Day":
                return "Tour",doc_date
            else:
                for l in tm_record:
                    if l.from_date == l.to_date:
                        if l.from_date_session == session:
                            return "Tour",doc_date
                        else: 
                            return False
                    else:
                        if l.from_date == doc_date:
                            if l.from_date_session == "Full Day" or l.from_date_session == session:
                                return "Tour",doc_date
                        elif l.to_date == doc_date and (l.to_date_session == "Full Day" or l.to_date_session == session):
                            return "Tour",doc_date
                        elif l.to_date > doc_date and l.from_date < doc_date:
                            return "Tour",doc_date
                        else:
                            return False
        else: 
            # Check if employee on C-Off
            coff_record = frappe.db.sql("""select from_date,to_date,from_date_session,to_date_session from `tabCompensatory Off Application`
                    where employee = %s and %s between from_date and to_date """, (employee, doc_date), as_dict=True)
            if coff_record:
                if session == "Full Day":
                    return "Coff",doc_date
                else:
                    for l in coff_record:
                        if l.from_date == l.to_date:
                            if l.from_date_session == session:
                                return "Coff",doc_date
                            else: 
                                return False
                        else:
                            if l.from_date == doc_date:
                                if l.from_date_session == "Full Day" or l.from_date_session == session:
                                    return "Coff",doc_date
                            elif l.to_date == doc_date and (l.to_date_session == "Full Day" or l.to_date_session == session):
                                return "Coff",doc_date
                            elif l.to_date > doc_date and l.from_date < doc_date:
                                return "Coff",doc_date
                            else:
                                return False
            else:
                leave_record = frappe.db.sql("""select from_date,to_date,from_date_session,to_date_session from `tabOn Duty Application`
                        where employee = %s and %s between from_date and to_date """, (employee, doc_date), as_dict=True)
                if leave_record:
                    if session == "Full Day":
                        return "OD",doc_date
                    else:
                        for l in leave_record:
                            if l.from_date == l.to_date:
                                if l.from_date_session == session:
                                    return "OD",doc_date
                                else: 
                                    return False
                            else:
                                if l.from_date == doc_date:
                                    if l.from_date_session == "Full Day" or l.from_date_session == session:
                                        return "OD",doc_date
                                elif l.to_date == doc_date and (l.to_date_session == "Full Day" or l.to_date_session == session):
                                    return "OD",doc_date
                                elif l.to_date > doc_date and l.from_date < doc_date:
                                    return "OD",doc_date
                                else:
                                    return False
                else:
                    return False

@frappe.whitelist()
def mark_hd():
    from_date = '2019-11-25'
    to_date = '2019-12-24'
    attendance = frappe.db.sql("""select att.working_shift as working_shift,att.name as name,att.status as status,att.admin_approved_status,att.late_in as late_in,att.early_out as early_out,att.first_half_status as first_half_status,att.second_half_status as second_half_status,att.name as name,att.employee_name as employee_name,att.attendance_date as attendance_date,att.work_time as work_time,att.overtime as overtime,att.employee as employee, att.employee_name as employee_name,att.status as status,att.in_time as in_time,att.out_time as out_time from `tabAttendance` att 
    where att.admin_approved_status is null and docstatus = 1 and att.attendance_date between %s and %s order by att.attendance_date""",(from_date,to_date),as_dict=1)
    for att in attendance:
        if att:
            addnl_work_time = timedelta(seconds=0)
            status = att.status
            fhs = att.first_half_status
            shs = att.second_half_status
            late_in = att.late_in
            early_out = att.early_out       
            working_shift = frappe.db.get_value("Employee", {'employee':att.employee},['working_shift']) 
            assigned_shift = frappe.db.sql("""select shift from `tabShift Assignment`
                        where employee = %s and %s between from_date and to_date""", (att.employee, att.attendance_date), as_dict=True)
            if assigned_shift:
                working_shift = assigned_shift[0]['shift']            
            if att.in_time:
                dt = datetime.strptime(att.in_time, "%d/%m/%Y %H:%M:%S")
                from_time = dt.time()
                shift_in_time = frappe.db.get_value("Working Shift",working_shift,"in_time")
                emp_in_time = timedelta(hours=from_time.hour,minutes=from_time.minute,seconds=from_time.second)
                #Check Movement Register
                if get_mr_in(att.employee,att.attendance_date):
                    mr_status_in = True
                    addnl_work_time += get_mr_in(att.employee,att.attendance_date)
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
                    addnl_work_time += get_mr_out(att.employee,att.attendance_date)
                    emp_out_time = emp_out_time + get_mr_out(att.employee,att.attendance_date)
                if emp_out_time < shift_out_time:
                    early_out = shift_out_time - emp_out_time
                else:
                    early_out = timedelta(seconds=0)

            if att.admin_approved_status == 'Present':
                late_in = early_out = timedelta(seconds=0)
            if att.admin_approved_status == 'First Half Present':
                late_in = timedelta(seconds=0)  
            if att.admin_approved_status == 'Second Half Present':
                early_out = timedelta(seconds=0) 
            if att.first_half_status == 'PR' and att.second_half_status == 'PR' and att.working_shift == 'FS3':
                late_in = early_out = timedelta(seconds=0)

            if att.status == "Present" or att.status == "Half Day":
                # print att.status,att.employee,att.attendance_date
                exc = frappe.db.get_list("Auto Present Employees",fields=['employee'])
                auto_present_list = []
                for e in exc:
                    auto_present_list.append(e.employee)
                if att.employee in auto_present_list:
                    fhs = shs = 'PR'
                elif late_in and late_in > timedelta(minutes=15) and early_out and early_out > timedelta(minutes=5):
                    fhs = shs = 'AB'
                    status = 'Absent'
                elif late_in and late_in > timedelta(minutes=15):
                    fhs = 'AB'
                    shs = 'PR'
                    status = 'Half Day'
                elif early_out and early_out > timedelta(minutes=5):
                    fhs = 'PR'
                    shs = 'AB'
                    status = 'Half Day'
                else:    
                    fhs = shs = 'PR'  
                    status = 'Present'
            update_wt = att.work_time
            if addnl_work_time:
                update_wt = att.work_time + addnl_work_time
            att_id = frappe.get_doc("Attendance",att.name)   
            att_id.update({
                "status":status,
                "first_half_status":fhs,
                "second_half_status":shs,
                "work_time":update_wt
            })    
            att_id.db_update()
            frappe.db.commit() 


@frappe.whitelist()
def temp_att():
    from_date = '2019-09-25'
    to_date = '2019-10-24'
    emp = '2037'
    # from_date = '2019-04-03'
    # to_date = '2019-04-03'
    attendance = frappe.db.sql("""select att.working_shift as working_shift,att.name as name,att.status as status,att.admin_approved_status,att.late_in as late_in,att.early_out as early_out,att.first_half_status as first_half_status,att.second_half_status as second_half_status,att.name as name,att.employee_name as employee_name,att.attendance_date as attendance_date,att.work_time as work_time,att.overtime as overtime,att.employee as employee, att.employee_name as employee_name,att.status as status,att.in_time as in_time,att.out_time as out_time from `tabAttendance` att 
    where att.admin_approved_status is null and docstatus = 1 and att.attendance_date between %s and %s order by att.attendance_date""",(from_date,to_date) ,as_dict=1)
    for att in attendance:
        if att:
            addnl_work_time = timedelta(seconds=0)
            status = att.status
            fhs = att.first_half_status
            shs = att.second_half_status
            late_in = att.late_in
            early_out = att.early_out       
            working_shift = frappe.db.get_value("Employee", {'employee':att.employee},['working_shift']) 
            assigned_shift = frappe.db.sql("""select shift from `tabShift Assignment`
                        where employee = %s and %s between from_date and to_date""", (att.employee, att.attendance_date), as_dict=True)
            if assigned_shift:
                working_shift = assigned_shift[0]['shift']            
            if att.in_time:
                dt = datetime.strptime(att.in_time, "%d/%m/%Y %H:%M:%S")
                from_time = dt.time()
                shift_in_time = frappe.db.get_value("Working Shift",working_shift,"in_time")
                emp_in_time = timedelta(hours=from_time.hour,minutes=from_time.minute,seconds=from_time.second)
                #Check Movement Register
                if get_mr_in(att.employee,att.attendance_date):
                    mr_status_in = True
                    addnl_work_time += get_mr_in(att.employee,att.attendance_date)
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
                    addnl_work_time += get_mr_out(att.employee,att.attendance_date)
                    emp_out_time = emp_out_time + get_mr_out(att.employee,att.attendance_date)
                if emp_out_time < shift_out_time:
                    early_out = shift_out_time - emp_out_time
                else:
                    early_out = timedelta(seconds=0)

            if att.admin_approved_status == 'Present':
                late_in = early_out = timedelta(seconds=0)
            if att.admin_approved_status == 'First Half Present':
                late_in = timedelta(seconds=0)  
            if att.admin_approved_status == 'Second Half Present':
                early_out = timedelta(seconds=0) 
            if att.first_half_status == 'PR' and att.second_half_status == 'PR' and att.working_shift == 'FS3':
                late_in = early_out = timedelta(seconds=0)

            if att.status == "Present" or att.status == "Half Day":
                # print att.status,att.employee,att.attendance_date
                exc = frappe.db.get_list("Auto Present Employees",fields=['employee'])
                auto_present_list = []
                for e in exc:
                    auto_present_list.append(e.employee)
                if att.employee in auto_present_list:
                    fhs = shs = 'PR'
                elif late_in and late_in > timedelta(minutes=15) and early_out and early_out > timedelta(minutes=5):
                    fhs = shs = 'AB'
                    status = 'Absent'
                elif late_in and late_in > timedelta(minutes=15):
                    fhs = 'AB'
                    shs = 'PR'
                    status = 'Half Day'
                elif early_out and early_out > timedelta(minutes=5):
                    fhs = 'PR'
                    shs = 'AB'
                    status = 'Half Day'
                else:    
                    fhs = shs = 'PR'  
                    status = 'Present'
            update_wt = att.work_time
            if addnl_work_time:
                update_wt = att.work_time + addnl_work_time
            att_id = frappe.get_doc("Attendance",att.name)   
            att_id.update({
                "status":status,
                "first_half_status":fhs,
                "second_half_status":shs,
                "work_time":update_wt
            })    
            att_id.db_update()
            frappe.db.commit() 

@frappe.whitelist()
def update_att_from_shift(employee,attendance_date,shift):
    attendance = frappe.db.sql("""select att.name as name,att.status as status,att.admin_approved_status,att.late_in as late_in,att.early_out as early_out,att.first_half_status as first_half_status,att.second_half_status as second_half_status,att.name as name,att.employee_name as employee_name,att.attendance_date as attendance_date,att.work_time as work_time,att.overtime as overtime,att.employee as employee, att.employee_name as employee_name,att.status as status,att.in_time as in_time,att.out_time as out_time from `tabAttendance` att 
    where  docstatus = 1 and employee = %s and attendance_date= %s """ % (employee,attendance_date), as_dict=1)
    for att in attendance:
        if att:
            status = att.status
            fhs = att.first_half_status
            shs = att.second_half_status
            late_in = att.late_in
            early_out = att.early_out       
            working_shift = shift
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

            if att.admin_approved_status == 'First Half Present':
                late_in = timedelta(seconds=0)  
            if att.admin_approved_status == 'Second Half Present':
                early_out = timedelta(seconds=0) 

            if att.status == "Present" or att.status == "Half Day":
                exc = frappe.db.get_list("Auto Present Employees",fields=['employee'])
                auto_present_list = []
                for e in exc:
                    auto_present_list.append(e.employee)
                if att.employee in auto_present_list:
                    fhs = shs = 'PR'
                elif late_in and late_in > timedelta(minutes=15) and early_out and early_out > timedelta(minutes=5):
                    fhs = shs = 'AB'
                    status = 'Absent'
                elif late_in and late_in > timedelta(minutes=15):
                    fhs = 'AB'
                    shs = 'PR'
                    status = 'Half Day'
                elif early_out and early_out > timedelta(minutes=5):
                    fhs = 'PR'
                    shs = 'AB'
                    status = 'Half Day'
                else:    
                    fhs = shs = 'PR'  
                    status = 'Present'
            
                   
            att_id = frappe.get_doc("Attendance",att.name)   
            att_id.update({
                "status":status,
                "first_half_status":fhs,
                "second_half_status":shs
            })    
            att_id.db_update()
            frappe.db.commit() 

# def get_mr_out(emp,day):
#     from_time = to_time = 0
#     dt = datetime.combine(day, datetime.min.time())
#     mrs = frappe.db.sql("""select from_time,to_time from `tabMovement Register` where employee= '%s' and docstatus=1 and status='Approved' and from_time between '%s' and '%s' """ % (emp,dt,add_days(dt,1)),as_dict=True)
#     for mr in mrs:
#         from_time = mr.from_time
#         to_time = mr.to_time
#     out_time = frappe.get_value("Attendance",{"employee":emp,"attendance_date":day},["out_time"])  
#     if out_time:
#         att_out_time = datetime.strptime(out_time,'%d/%m/%Y %H:%M:%S')
#         if from_time:
#             if att_out_time >= (from_time + timedelta(minutes=-10)) :
#                 return to_time - from_time

# def get_mr_in(emp,day):
#     from_time = to_time = 0
#     dt = datetime.combine(day, datetime.min.time())
#     mrs = frappe.db.sql("""select from_time,to_time from `tabMovement Register` where employee= '%s' and docstatus=1 and status='Approved' and from_time between '%s' and '%s' """ % (emp,dt,add_days(dt,1)),as_dict=True)
#     for mr in mrs:
#         from_time = mr.from_time
#         to_time = mr.to_time
#     in_time = frappe.get_value("Attendance",{"employee":emp,"attendance_date":day},["in_time"])
#     if in_time:    
#         att_in_time = datetime.strptime(in_time,'%d/%m/%Y %H:%M:%S')
#         if from_time:
#             if att_in_time >= (from_time + timedelta(minutes=-10)):
#                 return to_time - from_time