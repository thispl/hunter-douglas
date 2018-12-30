# -*- coding: utf-8 -*-
# Copyright (c) 2017, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import requests
import json
from datetime import datetime,timedelta,date
import datetime as dt
from frappe.utils import today,flt,add_days,date_diff,getdate
from frappe import _
import xml.etree.ElementTree as ET
from hunter_douglas.doctype.on_duty_application.on_duty_application import validate_if_attendance_not_applicable

@frappe.whitelist()	
def display_announcement(note,announcement):
    msgvar = """Notification.requestPermission(function (permission) 
    {
        if (permission === "granted")
     {  
         var notification = new Notification("%s"); 
         notification.onclick = function(event){
             event.preventDefault();
             frappe.set_route('Form','Announcements','%s')
         }
         }
          });""" % (note,announcement)
    user_list = frappe.get_all('User',filters={'enabled':1})
    for user in user_list:  
        frappe.publish_realtime(event='eval_js',message=msgvar,user=user['name'])

@frappe.whitelist()	
def send_birthday_wish():
    wish = frappe.db.sql("""select wish from `tabWishes`  order by RAND() limit 1""")
    msgvar = """Notification.requestPermission(function (permission) 
    {
        if (permission === "granted")
     {  
         var notification = new Notification("%s"); 
         }
          });""" % wish[0]
    user_list = frappe.get_all('User',filters={'enabled':1})
    for user in user_list:  
        frappe.publish_realtime(event='msgprint',message=wish[0],user=user['name'])
    # note = frappe.new_doc("Note")
    # note.title = 'Birthday Wishes'
    # note.public = 1
    # note.notify_on_login = 1
    # note.content = str(wish[0])
    # note.save(ignore_permissions=True)
    # frappe.db.commit()

@frappe.whitelist()
def fetch_att():
    preday = datetime.strptime(today(), '%Y-%m-%d')
    day = preday.strftime("%d%m%Y")
    # day = datetime.today().strftime("%d%m%Y")
    date = datetime.today().strftime("%Y-%m-%d")
    url = 'http://182.72.89.102/cosec/api.svc/attendance-daily?action=get;date-range=%s-%s;range=all;format=xml' % (day,day) 
    # url = 'http://182.72.89.102/cosec/api.svc/attendance-daily?action=get;date-range=27122018-27122018;range=all;format=xml'
    r = requests.get(url, auth=('sa', 'matrixx'))
    root = ET.fromstring(r.content)
    for att in root.findall('attendance-daily'):
        userid = att.find('UserID').text
        in_time = att.find('Punch1').text
        out_time = att.find('Punch2').text
        date = datetime.strptime((att.find('ProcessDate').text.replace("/","")), "%d%m%Y").date()
        date_f = date.strftime("%Y-%m-%d")
        work_time = timedelta(minutes=flt(att.find('WorkTime').text))
        over_time = timedelta(minutes=flt(att.find('Overtime').text))
        late_in = timedelta(minutes=flt(att.find('LateIn').text))
        early_out = timedelta(minutes=flt(att.find('EarlyOut').text))
        working_shift = att.find('WorkingShift').text
        employee = frappe.db.get_value("Employee", {
        "employee_number": userid, "status": "Active"})
        if employee:
            attendance_id = frappe.db.exists("Attendance", {
                "employee": employee, "attendance_date": date_f})
            if work_time > timedelta(seconds=1) :
                if work_time < timedelta(hours=5):
                    status = 'Half Day'
                else:    
                    status = 'Present'
            else:
                status = 'Absent'     
            if attendance_id:
                attendance = frappe.get_doc(
                    "Attendance", attendance_id)
                attendance.out_time = out_time
                attendance.in_time = in_time
                attendance.status = status
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
                    "employee": employee,
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

@frappe.whitelist()
def update_leave_approval(doc,status):
    lap = frappe.get_doc("Leave Application",doc)    
    lap.update({
        "status":status
    })
    lap.save(ignore_permissions=True)
    lap.submit()
    frappe.db.commit()

@frappe.whitelist()
def update_onduty_approval(doc,status):
    lap = frappe.get_doc("On Duty Application",doc)    
    lap.update({
        "status":status
    })
    lap.save(ignore_permissions=True)
    lap.submit()
    frappe.db.commit()

@frappe.whitelist()
def update_movement_register(doc,status):
    mr = frappe.get_doc("Movement Register",doc)  
    mr.update({
        "status":status
    })
    mr.save(ignore_permissions=True)
    mr.submit()
    frappe.db.commit()

@frappe.whitelist()
def update_travel_approval(doc,status):
    tm = frappe.get_doc("Travel Management",doc)  
    tm.update({
        "status":status
    })
    tm.save(ignore_permissions=True)
    tm.submit()
    frappe.db.commit()

@frappe.whitelist()
def update_expense_approval(doc,status):
    tm = frappe.get_doc("Expense Claim",doc)  
    tm.update({
        "workflow_state":status
    })
    tm.save(ignore_permissions=True)
    # tm.submit()
    frappe.db.commit()

@frappe.whitelist()
def update_tour_approval(doc,status):
    tm = frappe.get_doc("Tour Application",doc)  
    tm.update({
        "status":status
    })
    tm.save(ignore_permissions=True)
    tm.submit()
    frappe.db.commit()

@frappe.whitelist()
def update_tour_approval(doc,status):
    tm = frappe.get_doc("Tour Application",doc)  
    tm.update({
        "status":status
    })
    tm.save(ignore_permissions=True)
    tm.submit()
    frappe.db.commit()

@frappe.whitelist()
def bulk_leave_approve(names,status):
    if not frappe.has_permission("Leave Application","write"):
        frappe.throw(_("Not Permitted"),frappe.PermissionError)

    names = json.loads(names)
    for name in names:
        lap = frappe.get_doc("Leave Application",name)
        lap.update({
        "status":status
    })
    lap.save(ignore_permissions=True)
    lap.submit()
    frappe.db.commit()

@frappe.whitelist()
def bulk_travel_approve(names,status):
    if not frappe.has_permission("Travel Management","write"):
        frappe.throw(_("Not Permitted"),frappe.PermissionError)

    names = json.loads(names)
    for name in names:
        tm = frappe.get_doc("Travel Management",name)
        tm.update({
        "status":status
    })
    tm.save(ignore_permissions=True)
    tm.submit()
    frappe.db.commit()

@frappe.whitelist()
def bulk_onduty_approve(names,status):
    if not frappe.has_permission("On Duty Application","write"):
        frappe.throw(_("Not Permitted"),frappe.PermissionError)

    names = json.loads(names)
    for name in names:
        oda = frappe.get_doc("On Duty Application",name)
        oda.update({
        "status":status
    })
    oda.save(ignore_permissions=True)
    oda.submit()
    frappe.db.commit()

def update_website_context(context):
    context.update(dict(
        splash_image = '/assets/hunter_douglas/images/hd.svg'
    ))
    return context



@frappe.whitelist()
def auto_present():
    # for dt in daterange(date(2018, 11, 24), date(2018, 12, 29)):
    #     preday = dt
    preday = datetime.strptime(today(), '%Y-%m-%d')
    employee = []
    for emp in frappe.db.get_list("Auto Present Employees",fields=['employee']):
        doc = frappe.get_doc("Employee",emp['employee'])
        attendance = frappe.db.exists("Attendance", {"employee": emp['employee'], "attendance_date": preday})
        if attendance:
            frappe.db.set_value("Attendance",attendance,"status","Present")
            frappe.db.commit()
        else:
            attendance = frappe.new_doc("Attendance")
            attendance.employee = doc.employee
            attendance.employee_name = doc.employee_name
            attendance.status = "Present"
            attendance.attendance_date = dt
            # attendance.company = doc.company
            attendance.late_in = "00:00:00"
            attendance.work_time = "00:00:00"
            attendance.early_out = "00:00:00"
            attendance.overtime = "00:00:00"
            attendance.save(ignore_permissions=True)
            attendance.submit()
            frappe.db.commit()



def daterange(date1, date2):
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + timedelta(n)

@frappe.whitelist()

def fetch_test():
    preday = datetime.strptime(today(), '%Y-%m-%d')
    day = preday.strftime("%d%m%Y")
    # day = datetime.today().strftime("%d%m%Y")
    date = datetime.today().strftime("%Y-%m-%d")
    try:
         # url = 'http://182.72.89.102/cosec/api.svc/attendance-daily?action=get;date-range=%s-%s;range=all;format=xml' % (day,day) 
        url = 'http://182.72.89.102/cosec/api.svc/attendance-daily?action=get;date-range=22122018-22122018;range=all;format=xml'
        r = requests.get(url, auth=('sa', 'matrixx'))
        root = ET.fromstring(r.content)
        for att in root.findall('attendance-daily'):
            userid = att.find('UserID').text
            in_time = att.find('Punch1').text
            out_time = att.find('Punch2').text
            date = datetime.strptime((att.find('ProcessDate').text.replace("/","")), "%d%m%Y").date()
            date_f = date.strftime("%Y-%m-%d")
            work_time = timedelta(minutes=flt(att.find('WorkTime').text))
            over_time = timedelta(minutes=flt(att.find('Overtime').text))
            late_in = timedelta(minutes=flt(att.find('LateIn').text))
            early_out = timedelta(minutes=flt(att.find('EarlyOut').text))
            working_shift = att.find('WorkingShift').text
            employee = frappe.db.get_value("Employee", {
            "employee_number": userid, "status": "Active"})
            if employee:
                if not in_time and not out_time:
                    skip_attendance = validate_if_attendance_not_applicable(employee,date_f)
                    if skip_attendance:
                        print employee
                    if not skip_attendance:
                        attendance_id = frappe.db.exists("Attendance", {
                            "employee": employee, "attendance_date": date_f})
                        if work_time > timedelta(seconds=1) :
                            if work_time < timedelta(hours=5):
                                status = 'Half Day'
                            else:    
                                status = 'Present'
                        else:
                            status = 'Absent'     
                        if attendance_id:
                            attendance = frappe.get_doc(
                                "Attendance", attendance_id)
                            attendance.out_time = out_time
                            attendance.in_time = in_time
                            attendance.status = status
                            attendance.late_in = late_in
                            attendance.early_out = early_out
                            attendance.working_shift = working_shift
                            attendance.work_time = work_time
                            attendance.overtime = over_time
                            log_error("update attendance", userid)
                            attendance.db_update()
                            frappe.db.commit()
                        else:
                            attendance = frappe.new_doc("Attendance")
                            attendance.update({
                                "employee": employee,
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
    except requests.exceptions.ConnectionError as e:
        log_error("Connection Error", e)

def log_error(method, message):
    # employee = message["userid"]
	message = frappe.utils.cstr(message) + "\n" if message else ""
	d = frappe.new_doc("Error Log")
	d.method = method
	d.error = message
	d.insert(ignore_permissions=True)   