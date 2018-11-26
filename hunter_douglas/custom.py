# -*- coding: utf-8 -*-
# Copyright (c) 2017, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import requests
import json
from datetime import datetime,timedelta
import datetime as dt
from frappe.utils import today,flt,add_days,date_diff
from frappe import _
import xml.etree.ElementTree as ET


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
    preday = datetime.strptime(add_days(today(), -1), '%Y-%m-%d')
    day = preday.strftime("%d%m%Y")
    # day = datetime.today().strftime("%d%m%Y")
    date = datetime.today().strftime("%Y-%m-%d")
    url = 'http://182.72.89.102/cosec/api.svc/attendance-daily?action=get;date-range=%s-%s;range=all;format=xml' % (day,day) 
    # url = 'http://182.72.89.102/cosec/api.svc/attendance-daily?action=get;date-range=01102018-19112018;range=all;format=xml'
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
            attendance_id = frappe.db.get_value("Attendance", {
                "employee": employee, "attendance_date": date_f})
            if work_time > timedelta(seconds=1) :
                status = 'Present'
            else:
                status = 'Absent'     
            if attendance_id:
                attendance = frappe.get_doc(
                    "Attendance", attendance_id)
                attendance.out_time = out_time
                attendance.in_time = in_time
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
def update_att(doc,method):
    # date = doc.from_time.date()
    attendance = frappe.get_doc('Attendance',{"employee": doc.employee, "attendance_date": doc.from_time.date()} )
    attendance.update({
        "permission_in_time":doc.from_time,
        "permission_out_time":doc.to_time,
        "total_permission_hour":doc.total_permission_hour,
        "reason":doc.description
    })
    attendance.db_update()
    frappe.db.commit()
                    
@frappe.whitelist()
def on_duty_mark(doc,method):
    request_days = date_diff(doc.to_date, doc.from_date) + 1
    for number in range(request_days):
        attendance_date = add_days(doc.from_date, number)
        if attendance_date:
            attendance = frappe.new_doc("Attendance")
            attendance.update({
                "employee":doc.employee,
                "employee_name":doc.employee_name,
                "status":"Present",
                "attendance_date":attendance_date,
                "company":doc.company,
                "late_in":doc.late_in,
                "work_time":doc.work_time,
                "early_out":doc.early_out,
                "overtime":doc.overtime,
        })
        attendance.save(ignore_permissions=True)
        attendance.submit()
# @frappe.whitelist()
# def on_duty_mark(doc,method):
#     request_days = date_diff(doc.to_date, doc.from_date) + 1
#     for number in range(request_days):
#         attendance_date = add_days(doc.from_date, number)
#         if attendance_date:
#             attendance = frappe.new_doc("Attendance")
#             attendance.update({
#                 "employee":doc.employee,
#                 "employee_name":doc.employee_name,
#                 "status":"Present",
#                 "attendance_date":attendance_date,
#                 "company":doc.company,
#                 "late_in":doc.late_in,
#                 "work_time":doc.work_time,
#                 "early_out":doc.early_out,
#                 "overtime":doc.overtime,
#         })
#         attendance.save(ignore_permissions=True)
#         attendance.submit()