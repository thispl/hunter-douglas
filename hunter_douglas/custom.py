# -*- coding: utf-8 -*-
# Copyright (c) 2017, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import requests
import datetime
import json,calendar
from datetime import datetime,timedelta
import datetime as dt
from frappe.utils import today,flt,add_days,add_months,date_diff,getdate,formatdate,cint,cstr
from frappe.desk.notifications import delete_notification_count_for
from frappe import _
import xml.etree.ElementTree as ET
from hunter_douglas.doctype.on_duty_application.on_duty_application import validate_if_attendance_not_applicable


@frappe.whitelist()
def fetch_att_test(from_date,to_date):
    from_date = (datetime.strptime(str(from_date), '%Y-%m-%d')).date()
    to_date = (datetime.strptime(str(to_date), '%Y-%m-%d')).date()
    for preday in daterange(from_date, to_date):
        day = preday.strftime("%d%m%Y")
        date = datetime.today().strftime("%Y-%m-%d")
        exc = frappe.db.get_list("Auto Present Employees",fields=['employee'])
        auto_present_list = []
        for e in exc:
            auto_present_list.append(e.employee)
        employees = frappe.get_all('Employee',{'status':'Active','date_of_joining':('<=',preday)})
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
                url = 'http://10.19.8.248/cosec/api.svc/v2/attendance-daily?action=get;field-name=userid,ProcessDate,firsthalf,\
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
                            work_time = timedelta(minutes=flt(att.find('WorkTime').text))
                            over_time = timedelta(minutes=flt(att.find('Overtime').text))
                            late_in = timedelta(minutes=flt(att.find('LateIn').text))
                            early_out = timedelta(minutes=flt(att.find('EarlyOut').text))
                            working_shift = att.find('WorkingShift').text
                            attendance_id = frappe.db.exists("Attendance", {
                                "employee": emp.name, "attendance_date": date_f,"docstatus":1})
                            if work_time >= timedelta(hours=4) :
                                if work_time < timedelta(hours=7,minutes=45):
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

@frappe.whitelist()
def test():
    delete_notification_count_for("Chat")

def get_employees():            
    query = """SELECT employee,employee_name,designation FROM `tabEmployee` WHERE status='Active'
            ORDER BY employee"""
    data = frappe.db.sql(query, as_dict=1)
    return data

@frappe.whitelist()
def fetch_att():
    preday = datetime.strptime(today(), '%Y-%m-%d')
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
            url = 'http://10.19.8.248/cosec/api.svc/v2/attendance-daily?action=get;field-name=userid,ProcessDate,firsthalf,\
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
                        work_time = timedelta(minutes=flt(att.find('WorkTime').text))
                        over_time = timedelta(minutes=flt(att.find('Overtime').text))
                        late_in = timedelta(minutes=flt(att.find('LateIn').text))
                        early_out = timedelta(minutes=flt(att.find('EarlyOut').text))
                        working_shift = att.find('WorkingShift').text
                        attendance_id = frappe.db.exists("Attendance", {
                            "employee": emp.name, "attendance_date": date_f,"docstatus":1})
                        if work_time >= timedelta(hours=4) :
                            if work_time < timedelta(hours=7,minutes=45):
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

# @frappe.whitelist()
# def fetch_att():
#     preday = datetime.strptime(today(), '%Y-%m-%d')
#     day = preday.strftime("%d%m%Y")
#     # date = datetime.today().strftime("%Y-%m-%d")
#     exc = frappe.db.get_list("Auto Present Employees",fields=['employee'])
#     auto_present_list = []
#     for e in exc:
#         auto_present_list.append(e.employee)
#     employees = frappe.get_all('Employee',{'status':'Active'})
#     for emp in employees:
#         if emp.name in auto_present_list:
#             doc = frappe.get_doc("Employee",emp.name)
#             attendance = frappe.db.exists("Attendance", {"employee": doc.employee, "attendance_date": preday})
#             if attendance:
#                 frappe.db.set_value("Attendance",attendance,"status","Present")
#                 frappe.db.commit()
#             else:
#                 attendance = frappe.new_doc("Attendance")
#                 attendance.employee = doc.employee
#                 attendance.employee_name = doc.employee_name
#                 attendance.status = "Present"
#                 attendance.attendance_date = preday
#                 # attendance.company = doc.company
#                 attendance.working_shift = frappe.get_value("Employee",emp.name,"working_shift"),
#                 attendance.late_in = "00:00:00"
#                 attendance.work_time = "00:00:00"
#                 attendance.early_out = "00:00:00"
#                 attendance.overtime = "00:00:00"
#                 attendance.save(ignore_permissions=True)
#                 attendance.submit()
#                 frappe.db.commit()
#         else:
#             url = 'http://10.19.8.248/cosec/api.svc/v2/attendance-daily?action=get;field-name=userid,ProcessDate,firsthalf,\
#                     secondhalf,punch1,punch2,workingshift,shiftstart,shiftend,latein,earlyout,worktime,overtime;date-range=%s-%s;range=user;id=%s;format=xml' % (day,day,emp.name) 
#             r = requests.get(url, auth=('sa', 'matrixx'))
#             if "No records found" in r.content:
#                 attendance_id = frappe.db.exists("Attendance", {
#                         "employee": emp.name, "attendance_date": preday,"docstatus":1})
#                 if attendance_id:
#                     pass
#                 else:            
#                     attendance = frappe.new_doc("Attendance")
#                     attendance.update({
#                         "employee": emp.name,
#                         "attendance_date": preday,
#                         "status": 'Absent',
#                         "late_in" : "0:00:00",
#                         "early_out" : "0:00:00",
#                         "working_shift" : frappe.get_value("Employee",emp.name,"working_shift"),
#                         "work_time": "0:00:00",
#                         "overtime":"0:00:00"
#                     })
#                     attendance.save(ignore_permissions=True)
#                     attendance.submit()
#                     frappe.db.commit() 
#             else:    
#                 root = ET.fromstring(r.content)
#                 for att in root.findall('attendance-daily'):
#                     userid = att.find('UserID').text
#                     in_time = att.find('Punch1').text
#                     out_time = att.find('Punch2').text
#                     first_half_status = att.find('firsthalf').text
#                     second_half_status = att.find('secondhalf').text
#                     date = datetime.strptime((att.find('ProcessDate').text.replace("/","")), "%d%m%Y").date()
#                     date_f = date.strftime("%Y-%m-%d")
#                     work_time = timedelta(minutes=flt(att.find('WorkTime').text))
#                     over_time = timedelta(minutes=flt(att.find('Overtime').text))
#                     late_in = timedelta(minutes=flt(att.find('LateIn').text))
#                     early_out = timedelta(minutes=flt(att.find('EarlyOut').text))
#                     working_shift = att.find('WorkingShift').text
#                     attendance_id = frappe.db.exists("Attendance", {
#                         "employee": emp.name, "attendance_date": date_f,"docstatus":1})
#                     if work_time > timedelta(seconds=1) :
#                         if work_time < timedelta(hours=5):
#                             status = 'Half Day'
#                         else:    
#                             status = 'Present'
#                     else:
#                         status = 'Absent'     
#                     if attendance_id:
#                         attendance = frappe.get_doc(
#                             "Attendance", attendance_id)
#                         attendance.out_time = out_time
#                         attendance.in_time = in_time
#                         attendance.status = status
#                         attendance.first_half_status = first_half_status
#                         attendance.second_half_status = second_half_status
#                         attendance.late_in = late_in
#                         attendance.early_out = early_out
#                         attendance.working_shift = working_shift
#                         attendance.work_time = work_time
#                         attendance.overtime = over_time
#                         attendance.db_update()
#                         frappe.db.commit()
#                     else:
#                         attendance = frappe.new_doc("Attendance")
#                         attendance.update({
#                             "employee": emp.name,
#                             "attendance_date": date_f,
#                             "status": status,
#                             "in_time": in_time,
#                             "late_in" : late_in,
#                             "early_out" : early_out,
#                             "working_shift" : working_shift,
#                             "out_time": out_time,
#                             "work_time": work_time,
#                             "overtime":over_time
#                         })
#                         attendance.save(ignore_permissions=True)
#                         attendance.submit()
#                         frappe.db.commit()
   
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
    tm = frappe.get_doc("Movement Register",doc)  
    tm.update({
        "status":status
    })
    tm.save(ignore_permissions=True)
    tm.submit()
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
    

# @frappe.whitelist()
# def update_tour_approval(doc,status):
#     tm = frappe.get_doc("Tour Application",doc)  
#     tm.update({
#         "status":status
#     })
#     tm.save(ignore_permissions=True)
#     tm.submit()
#     frappe.db.commit()

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
def bulk_auto_present():
    for preday in daterange(date(2019, 1, 10), date(2019, 1, 10)):
    # #     preday = dt
    # preday = datetime.strptime(today(), '%Y-%m-%d').date()
        employee = []
        for emp in frappe.db.get_list("Auto Present Employees",fields=['employee']):
            # skip_attendance = validate_if_attendance_not_applicable(emp,preday)
            # if not skip_attendance:
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
                attendance.attendance_date = preday
                # attendance.company = doc.company
                attendance.late_in = "00:00:00"
                attendance.work_time = "00:00:00"
                attendance.early_out = "00:00:00"
                attendance.overtime = "00:00:00"
                attendance.save(ignore_permissions=True)
                attendance.submit()
                frappe.db.commit()



def daterange(date1,date2):
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + timedelta(n)

def log_error(method, message):
    # employee = message["userid"]
    message = frappe.utils.cstr(message) + "\n" if message else ""
    d = frappe.new_doc("Error Log")
    d.method = method
    d.error = message
    d.insert(ignore_permissions=True)   

@frappe.whitelist()
def validate_if_attendance_not_applicable(employee, attendance_date):
    frappe.errprint("hi")
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

@frappe.whitelist()
def in_punch_alert():
    day =  today()
    exc = frappe.db.get_list("Auto Present Employees",fields=['employee'])
    employees_list = []
    for e in exc:
        employees_list.append(e.employee)
    employees = frappe.get_all('Employee',{'status':'Active'})
    for emp in employees:
        if emp.name not in employees_list:
            skip_attendance = validate_if_attendance_not_applicable(emp.name,day)
            if not skip_attendance:
                frappe.sendmail(
                    recipients=['sivaranjani.s@voltechgroup.com'],
                    subject='Missed IN Punch Alert for %s' +
                    formatdate(today()),
                    message=""" 
                    <h3>Missed In Punch Alert</h3>
                    <p>Dear %s,</p>
                    <h4>Info:</h4>
                    <p>This is the reminder for Missed In Punch for today %s</p>
                    """ % (frappe.get_value("Employee",emp.name,"employee_name"),formatdate(day))
                    )    
                att = frappe.db.exists("Attendance",{"employee":emp.name,"attendance_date":day})
                if not att:
                    attendance = frappe.new_doc("Attendance")
                    attendance.update({
                        "employee": emp.name,
                        "attendance_date": day,
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

@frappe.whitelist()
def out_punch_alert():
    day =  today()
    exc = frappe.db.get_list("Auto Present Employees",fields=['employee'])
    employees_list = []
    for e in exc:
        employees_list.append(e.employee)
    employees = frappe.get_all('Employee',{'status':'Active'})
    for emp in employees:
        if emp.name not in employees_list:
            att_record = frappe.db.sql("""select name from `tabAttendance`
            where employee = %s and in_time > '0' and out_time is null and attendance_date = %s
            and docstatus = 1""", (emp.name, day), as_dict=True)
            if att_record:
                frappe.sendmail(
                    recipients=['sivaranjani.s@voltechgroup.com'],
                    subject='Missed Out Punch Alert for %s' +
                    formatdate(today()),
                    message=""" 
                    <h3>Missed Out Punch Alert</h3>
                    <p>Dear %s,</p>
                    <h4>Info:</h4>
                    <p>This is the reminder for Missed Out Punch for today %s</p>
                    """ % (frappe.get_value("Employee",emp.name,"employee_name"),formatdate(day))
                    )     

@frappe.whitelist()
def continuous_absentees():
    # day =  today()
    exc = frappe.db.get_list("Auto Present Employees",fields=['employee'])
    employees_list = []
    for e in exc:
        employees_list.append(e.employee)
    query = """select name,employee,attendance_date from `tabAttendance` where \
    status='Absent' and attendance_date between '%s' and '%s' """ % (add_days(today(),-3),today())
    employees = frappe.db.sql(query,as_dict=True) 
    for emp in employees:
        if emp.employee not in employees_list:
            print emp


def validate_if_attendance_not_applicable(employee, attendance_date):
    # Check if attendance is Present
    att_record = frappe.db.sql("""select name from `tabAttendance`
            where employee = %s and in_time > '0' and attendance_date = %s
            and docstatus = 1""", (employee, attendance_date), as_dict=True)
    if att_record:
        return "att",True        
    # Check if attendance_date is a Holiday
    if is_holiday(employee, attendance_date):
        return "holiday",True
    # Check if employee on Leave
    leave_record = frappe.db.sql("""select half_day from `tabLeave Application`
            where employee = %s and %s between from_date and to_date
            and docstatus = 1""", (employee, attendance_date), as_dict=True)
    if leave_record:
        return "leave",True
    # Check if employee on On-Duty
    od_record = frappe.db.sql("""select half_day from `tabOn Duty Application`
            where employee = %s and %s between from_date and to_date
            and docstatus = 1""", (employee, attendance_date), as_dict=True)
    if od_record:
        return "od",True    
    # Check if employee on On-Travel
    tm_record = frappe.db.sql("""select half_day from `tabTravel Management`
            where employee = %s and %s between from_date and to_date
            and docstatus = 1""", (employee, attendance_date), as_dict=True)
    if tm_record:
        return "tm",True     

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


def calculate_comp_off():
    day = add_days(today(),-1)
    from_date = (datetime.strptime('2018-12-25', '%Y-%m-%d')).date()
    to_date = (datetime.strptime('2019-01-24', '%Y-%m-%d')).date()
    for preday in daterange(from_date,to_date):
        for emp in frappe.get_all("Employee",{"status":"Active","coff_eligible":1}):
            if is_holiday(emp, preday):
                coff_hours = frappe.get_value("Attendance",{"attendance_date":preday,"employee":emp.name},["work_time"])
                if coff_hours:
                    coff_id = frappe.db.exists("Comp Off Balance",{"employee":emp.name,"comp_off_date":preday})
                    if coff_id:
                        coff = frappe.get_doc("Comp Off Balance",coff_id)
                    else:    
                        coff = frappe.new_doc("Comp Off Balance")
                    coff.update({
                        "employee":emp.name,
                        "hours":coff_hours,
                        "comp_off_date":preday,
                        "validity":add_months(preday,3)
                    })
                    coff.save(ignore_permissions=True)
                    frappe.db.commit()

@frappe.whitelist()
def get_coff(employee):
    t_hours = 0
    coff_hours = sum([flt(d.hours.total_seconds()) for d in frappe.get_all("Comp Off Balance",{"employee":employee,"expired":0},["hours"])])
    hours = coff_hours//3600
    minutes = (coff_hours%3600) // 60
    t_hours = timedelta(hours=hours,minutes=minutes)
    return t_hours

@frappe.whitelist()
def att_adjust(employee,attendance_date,name,in_time,out_time,status_p,status_a,status_ph,status_wo,status_first_half_present,status_second_half_present):
    if name:
        itime = otime = ""
        att = frappe.get_doc("Attendance",name)
        fdate = datetime.strptime(attendance_date,'%Y-%m-%d').strftime('%d/%m/%Y')
        if in_time:
            itime = fdate + ' '+ in_time
        if out_time:    
            otime = fdate + ' '+ out_time
        if att and status_p == "1":
            att.update({
                "status":"Present",
                "admin_approved_status": "Present",
                "in_time": itime,
                "out_time": otime
            })
            att.save(ignore_permissions=True)
            frappe.db.commit()
        elif att and status_a == "1":
            att.update({
                "status":"Absent",
                "admin_approved_status": "Absent",
                "in_time": itime,
                "out_time": otime
            })
            att.save(ignore_permissions=True)
            frappe.db.commit()
        elif att and status_ph == "1":
            att.update({
                "status":"Absent",
                "admin_approved_status": "PH",
                "in_time": itime,
                "out_time": otime
            })
            att.save(ignore_permissions=True)
            frappe.db.commit()
        elif att and status_wo == "1":
            att.update({
                "status":"Absent",
                "admin_approved_status": "WO",
                "in_time": itime,
                "out_time": otime
            })
            att.save(ignore_permissions=True)
            frappe.db.commit()
        elif att and status_first_half_present == "1":
            if att.status == 'Half Day':
                att.update({
                    "status":"Present",
                    "first_half_status":"PR",
                    "admin_approved_status": "First Half Present",
                    "in_time": itime,
                    "out_time": otime
                }) 
            if att.status == 'Absent':
                att.update({
                    "status":"Half Day",
                    "first_half_status":"PR",
                    "admin_approved_status": "First Half Present",
                    "in_time": itime,
                    "out_time": otime
                })     
            att.save(ignore_permissions=True)
            frappe.db.commit()   
        elif att and status_second_half_present == "1":
            if att.status == 'Half Day':
                att.update({
                    "status":"Present",
                    "second_half_status":"PR",
                    "admin_approved_status": "Second Half Present",
                    "in_time": itime,
                    "out_time": otime
                }) 
            if att.status == 'Absent':
                att.update({
                    "status":"Half Day",
                    "second_half_status":"PR",
                    "admin_approved_status": "Second Half Present",
                    "in_time": itime,
                    "out_time": otime
                })
            att.save(ignore_permissions=True)
            frappe.db.commit()      
        elif att and in_time or out_time:
            att.update({
                "admin_approved_status": "Present",
                "in_time": itime,
                "out_time": otime
            })
            att.save(ignore_permissions=True)
            frappe.db.commit()
    return True


@frappe.whitelist()
def bulk_att_adjust(employee,from_date,to_date,status):
    if employee:
        att = frappe.db.sql("""select name from `tabAttendance`
                where employee=%s
                and attendance_date between %s and %s""", (employee, from_date, to_date), as_dict=1)
        for a in att:
            if a:
                att = frappe.get_doc("Attendance",a)
                if att:
                    att.update({
                        "admin_approved_status": status
                    })
                    frappe.errprint(att.admin_approved_status)
                    att.save(ignore_permissions=True)
                    frappe.db.commit()
        return True

@frappe.whitelist()
def bulk_admin_att():
    attendance = frappe.get_all("Attendance",{"admin_approved_status":"Present"})
    for att in attendance:
        att1 = frappe.get_doc("Attendance",att)
        att1.update({
            "status":'Present'
        })
        att1.db_update()
        frappe.db.commit()


@frappe.whitelist()
def fetch_att_temp():
    from_date = (datetime.strptime('2019-01-07', '%Y-%m-%d')).date()
    to_date = (datetime.strptime('2019-01-24', '%Y-%m-%d')).date()
    emp = '1316'
    for preday in daterange(from_date,to_date):
        day = preday.strftime("%d%m%Y")
        url = 'http://10.19.8.248/cosec/api.svc/v2/attendance-daily?action=get;field-name=userid,ProcessDate,firsthalf,\
                            secondhalf,punch1,punch2,workingshift,shiftstart,shiftend,latein,earlyout,worktime,overtime;date-range=%s-%s;range=user;id=1315;format=xml' % (day,day) 
        r = requests.get(url, auth=('sa', 'matrixx'))
        if "No records found" in r.content:
            attendance_id = frappe.db.exists("Attendance", {
                    "employee": emp, "attendance_date": preday,"docstatus":1})
            if attendance_id:
                pass
            else:            
                attendance = frappe.new_doc("Attendance")
                attendance.update({
                    "employee": emp,
                    "attendance_date": preday,
                    "status": 'Absent',
                    "late_in" : "0:00:00",
                    "early_out" : "0:00:00",
                    "working_shift" : frappe.get_value("Employee",emp,"working_shift"),
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
                    work_time = timedelta(minutes=flt(att.find('WorkTime').text))
                    over_time = timedelta(minutes=flt(att.find('Overtime').text))
                    late_in = timedelta(minutes=flt(att.find('LateIn').text))
                    early_out = timedelta(minutes=flt(att.find('EarlyOut').text))
                    working_shift = att.find('WorkingShift').text
                    attendance_id = frappe.db.exists("Attendance", {
                        "employee": emp, "attendance_date": date_f,"docstatus":1})
                    if work_time >= timedelta(hours=4) :
                        if work_time < timedelta(hours=7,minutes=45):
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
                            "employee": emp,
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
                 