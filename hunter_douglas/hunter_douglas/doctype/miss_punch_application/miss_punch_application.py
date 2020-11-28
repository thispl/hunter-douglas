# -*- coding: utf-8 -*-
# Copyright (c) 2019, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
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


class MissPunchApplication(Document):
    def on_submit(self):
        if self.status == "Approved": 
            update_attendance_by_mp(self.employee,self.attendance_date,self.in_time,self.out_time)



@frappe.whitelist()
def check_attendance(employee,attendance_date):
    att_in_time = att_out_time = 0
    if frappe.db.exists("Attendance", {"employee": employee,"attendance_date": attendance_date}):
        att = frappe.get_doc("Attendance",{"employee": employee,"attendance_date": attendance_date})
        if att:
            if att.in_time:
                att_in = datetime.strptime(att.in_time,"%d/%m/%Y %H:%M:%S")
                att_in_time = att_in.strftime("%H:%M:%S")
            if att.out_time:
                att_out = datetime.strptime(att.out_time,"%d/%m/%Y %H:%M:%S")
                att_out_time = att_out.strftime("%H:%M:%S")    
                
            return att_in_time,att_out_time
    else:
        return "OK"

@frappe.whitelist()
def update_attendance_by_mp(employee,attendance_date,in_time,out_time):
    working_shift = frappe.db.get_value("Employee", {'employee':employee},['working_shift']) 
    assigned_shift = frappe.db.sql("""select shift from `tabShift Assignment`
                where employee = %s and %s between from_date and to_date""", (employee, attendance_date), as_dict=True)
    if assigned_shift:
        working_shift = assigned_shift[0]['shift']
    status = "Present"
    nd = get_att_data(employee,attendance_date,working_shift,in_time,out_time,status)
    first_half_status = nd.first_half_status
    second_half_status = nd.second_half_status
    status = nd.status
    late_in = nd.late_in
    early_out = nd.early_out
    work_time = timedelta(minutes=cint(nd.work_time))
    over_time = timedelta(minutes=cint(nd.over_time))
    if in_time:
        att_in = attendance_date.strftime("%d/%m/%Y")
        att_in_time = str(att_in) + ' ' +str(in_time)
    if out_time:
        att_out = attendance_date.strftime("%d/%m/%Y")
        att_out_time = str(att_out) + ' ' +str(out_time)
    attendance_id = frappe.db.exists("Attendance", {
                                "employee": employee, "attendance_date": attendance_date,"docstatus":1})
    if attendance_id:
        attendance = frappe.get_doc(
            "Attendance", attendance_id)
        attendance.out_time = att_out_time
        attendance.in_time = att_in_time
        attendance.status = status 
        attendance.first_half_status = first_half_status
        attendance.second_half_status = second_half_status
        attendance.late_in = late_in
        attendance.early_out = early_out
        attendance.working_shift = working_shift
        attendance.work_time = work_time
        attendance.overtime = over_time
        attendance.modified_status = "Miss Punch"
        attendance.db_update()
        frappe.db.commit()
    else:
        attendance = frappe.new_doc("Attendance")
        attendance.update({
            "employee": employee,
            "attendance_date": attendance_date,
            "status": status,
            "in_time": att_in_time,
            "late_in" : late_in,
            "early_out" : early_out,
            "working_shift" : working_shift,
            "out_time": att_out_time,
            "work_time": work_time,
            "overtime":over_time,
            "first_half_status": first_half_status,
            "second_half_status":second_half_status,
            "modified_status": "Miss Punch"
        })
        attendance.save(ignore_permissions=True)
        attendance.submit()
        frappe.db.commit()  

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
        # dt = datetime.strptime(in_time, "%d/%m/%Y %H:%M:%S")
        # from_time = dt.time()       
        emp_in_time = in_time
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
            # dt = datetime.strptime(out_time, "%d/%m/%Y %H:%M:%S")
            # end_time = dt.time()
            emp_out_time = out_time
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
        out_time_f = out_time
        in_time_f = in_time
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