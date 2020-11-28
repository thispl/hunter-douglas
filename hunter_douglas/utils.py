# -*- coding: utf-8 -*-
# Copyright (c) 2017, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import requests
import json,calendar
from datetime import datetime,timedelta,time
import datetime as dt
from frappe.utils import today,flt,add_days,add_months,date_diff,getdate,formatdate,cint,cstr
from frappe import _
import xml.etree.ElementTree as ET

@frappe.whitelist()
def validate_if_attendance_not_applicable(employee, attendance_date):
    # Check if attendance_date is a Holiday
    if is_holiday(employee, attendance_date):
        return True
    # Check if employee on Leave
    leave_record = frappe.db.sql("""select half_day from `tabLeave Application`
            where employee = %s and %s between from_date and to_date
            and docstatus = 1""", (employee, attendance_date), as_dict=True)
    if leave_record:
        return True

    return False

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

@frappe.whitelist()
def fetch_att():
    from_date = (datetime.strptime('2019-02-26', '%Y-%m-%d')).date()
    to_date = (datetime.strptime('2019-02-26', '%Y-%m-%d')).date()
    for preday in daterange(from_date,to_date):
        day = preday.strftime("%d%m%Y")
        exc = frappe.db.get_list("Auto Present Employees",fields=['employee'])
        auto_present_list = []
        for e in exc:
            auto_present_list.append(e.employee)
        employees = frappe.get_all('Employee',{'status':'Active'})
        for emp in employees:
            if emp.name in auto_present_list:
                doc = frappe.get_doc("Employee",emp.name)
                attendance = frappe.db.exists("Attendance", {"employee": doc.employee, "attendance_date": preday})
                if attendance:
                    frappe.db.set_value("Attendance",attendance,"status","Present")
                    frappe.db.commit()
                else:
                    attendance = frappe.new_doc("Attendance")
                    attendance.employee = doc.employee
                    attendance.employee_name = doc.employee_name
                    attendance.status = "Present"
                    attendance.attendance_date = preday
                    # attendance.company = doc.company
                    attendance.working_shift = frappe.get_value("Employee",emp.name,"working_shift"),
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
                    attendance_id = frappe.db.exists("Attendance", {
                            "employee": emp.name, "attendance_date": preday,"docstatus":1})
                    if attendance_id:
                        pass
                    else:            
                        attendance = frappe.new_doc("Attendance")
                        attendance.update({
                            "employee": emp.name,
                            "attendance_date": preday,
                            "status": 'Absent',
                            "late_in" : "0:00:00",
                            "early_out" : "0:00:00",
                            "working_shift" : frappe.get_value("Employee",emp.name,"working_shift"),
                            "work_time": "0:00:00",
                            "overtime":"0:00:00"
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
                            first_half_status = att.find('firsthalf').text
                            second_half_status = att.find('secondhalf').text
                            date = datetime.strptime((att.find('ProcessDate').text.replace("/","")), "%d%m%Y").date()
                            date_f = date.strftime("%Y-%m-%d")
                            if flt(att.find('WorkTime').text) > 1440:
                                work_time = timedelta(minutes=flt('1400'))
                            else:
                                work_time = timedelta(minutes=flt(att.find('WorkTime').text))    
                            over_time = timedelta(minutes=flt(att.find('Overtime').text))
                            late_in = timedelta(minutes=flt(att.find('LateIn').text))
                            early_out = timedelta(minutes=flt(att.find('EarlyOut').text))
                            working_shift = att.find('WorkingShift').text
                            attendance_id = frappe.db.exists("Attendance", {
                                "employee": emp.name, "attendance_date": date_f,"docstatus":1})
                               
                            if out_time:
                                out_time_f = datetime.strptime(out_time, "%d/%m/%Y %H:%M:%S")
                            if in_time:    
                                in_time_f = datetime.strptime(in_time, "%d/%m/%Y %H:%M:%S")
                            if in_time and out_time:
                                work_time = out_time_f - in_time_f     
                            wt_seconds = work_time.total_seconds() // 60
                            if wt_seconds > 1440:
                                work_time = timedelta(minutes=flt('1400'))     

                            if work_time >= timedelta(hours=4):
                                if work_time < timedelta(hours=7,minutes=45):
                                    status = 'Half Day'
                                else:    
                                    status = 'Present'
                            else:
                                status = 'Absent'    
                            
                            # print userid
                            # print in_time
                            # print out_time
                            # print work_time
                            # print day     
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
                                    "overtime":over_time
                                })
                                attendance.save(ignore_permissions=True)
                                attendance.submit()
                                frappe.db.commit() 

def daterange(date1,date2):
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + timedelta(n)

@frappe.whitelist()
def mark_exp_paid(names,paid_date):
    names = json.loads(names)
    for name in names:
        exp = frappe.get_doc("Expense Claim",name)
        if exp.is_paid == 0 and exp.docstatus == 1 and exp.approval_status == 'Approved':
            exp.update({
                "is_paid": 1,
                "paid_date":paid_date,
                "workflow_state":'Claim Paid'
            })
            exp.save(ignore_permissions=True)
            # emp.submit()
            frappe.db.commit()


