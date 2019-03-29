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
from frappe.utils import today,flt,add_days,add_months,date_diff,getdate,formatdate,cint,cstr
from frappe.desk.notifications import delete_notification_count_for
from frappe import _
import xml.etree.ElementTree as ET
from hunter_douglas.doctype.on_duty_application.on_duty_application import validate_if_attendance_not_applicable
from frappe.email.email_body import (replace_filename_with_cid,
    get_email, inline_style_in_html, get_header)


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
            working_shift = frappe.db.get_value("Employee", {'employee':emp.name},['working_shift']) 
            assigned_shift = frappe.db.sql("""select shift from `tabShift Assignment`
                        where employee = %s and %s between from_date and to_date""", (emp.name, preday), as_dict=True)
            if assigned_shift:
                working_shift = assigned_shift[0]['shift']
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
                    attendance.working_shift = working_shift,
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
                            "working_shift" : working_shift,
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
        working_shift = frappe.db.get_value("Employee", {'employee':emp.name},['working_shift']) 
        assigned_shift = frappe.db.sql("""select shift from `tabShift Assignment`
                    where employee = %s and %s between from_date and to_date""", (emp.name, preday), as_dict=True)
        if assigned_shift:
            working_shift = assigned_shift[0]['shift']
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
                        "working_shift" : working_shift,
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
def fetch_employee():
    url = 'http://182.72.89.102/cosec/api.svc/v2/user?action=get;format=xml' 
    r = requests.get(url, auth=('sa', 'matrixx'))
    root = ET.fromstring(r.content)
    for emp in root.findall('user'):
        reference_code = emp.find('reference-code').text
        if reference_code == "1309":
            if not frappe.db.exists("Employee","1309"):
                employee = frappe.new_doc("Employee")
                employee.update({
                    "employee_name": emp.find('name').text,
                    "employee_number": emp.find('reference-code').text,
                    "date_of_joining": (datetime.strptime(emp.find('joining-date').text, '%d%m%Y')).date(),
                    # "date_of_birth" : emp.find('date-of-birth').text,
                    "gender" : "Male",
                    "reports_to" : emp.find('rg_incharge_1').text,
                    "leave_approver": emp.find('rg_incharge_1').text,
                    # "prefered_contact_email": emp.find('official-email').text,
                    "passport_number":emp.find('passport-no').text,
                    "pf_number":emp.find('pf-no').text,
                    "pan_number":emp.find('pan').text,
                    "uan_number":emp.find('uan').text
                })
                employee.save(ignore_permissions=True)
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
    
    # """Send Employee birthday reminders if no 'Stop Birthday Reminders' is not set."""
    # if int(frappe.db.get_single_value("HR Settings", "stop_birthday_reminders") or 0):
    # 	return
    from frappe.utils.user import get_enabled_system_users
    users = None
    birthdays = get_employees_who_are_born_today()
    wish = frappe.db.sql("""select wish from `tabWishes`  order by RAND() limit 1""",as_dict=1)[0]
    if birthdays:
        if not users:
            users = [u.email_id or u.name for u in get_enabled_system_users()]
        for e in birthdays:
            age = calculate_age(e.date_of_birth)
            args = dict(employee=e.employee_name,age=age,wish=wish['wish'],company=frappe.defaults.get_defaults().company)
            # frappe.sendmail(recipients=filter(lambda u: u not in (e.company_email, e.personal_email, e.user_id), users),
            frappe.sendmail(recipients=['sivaranjani.s@voltechgroup.com'],
                subject=_("Birthday Reminder for {0}").format(e.employee_name),
                # message=_("""Today is {0}'s birthday!""").format(e.employee_name),
                template = 'birthday_wish',
                args = args)

def calculate_age(dtob):
    today = date.today()
    return today.year - dtob.year - ((today.month, today.day) < (dtob.month, dtob.day))

def get_employees_who_are_born_today():
    """Get Employee properties whose birthday is today."""
    return frappe.db.sql("""select name,date_of_birth, personal_email, company_email, user_id, employee_name
        from tabEmployee where day(date_of_birth) = day(%(date)s)
        and month(date_of_birth) = month(%(date)s)
        and status = 'Active'""", {"date": today()}, as_dict=True)    

    # msgvar = """Notification.requestPermission(function (permission) 
    # {
    #     if (permission === "granted")
    #  {  
    #      var notification = new Notification("%s"); 
    #      }
    #       });""" % wish[0]
    # user_list = frappe.get_all('User',filters={'enabled':1})
    # for user in user_list:  
    #     frappe.publish_realtime(event='msgprint',message=wish[0],user=user['name'])
    # note = frappe.new_doc("Note")
    # note.title = 'Birthday Wishes'
    # note.public = 1
    # note.notify_on_login = 1
    # note.content = str(wish[0])
    # note.save(ignore_permissions=True)
    # frappe.db.commit()

   
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
    # day = add_days(today(),-1)
    # from_date = (datetime.strptime('2018-12-25', '%Y-%m-%d')).date()
    # to_date = (datetime.strptime('2019-01-24', '%Y-%m-%d')).date()
    # for preday in daterange(from_date,to_date):
    #     for emp in frappe.get_all("Employee",{"status":"Active","coff_eligible":1}):
    #         if is_holiday(emp, preday):
    #             coff_hours = frappe.get_value("Attendance",{"attendance_date":preday,"employee":emp.name},["work_time"])
    #             if coff_hours:
    #                 coff_id = frappe.db.exists("Comp Off Balance",{"employee":emp.name,"comp_off_date":preday})
    #                 if coff_id:
    #                     coff = frappe.get_doc("Comp Off Balance",coff_id)
    #                 else:    
    #                     coff = frappe.new_doc("Comp Off Balance")
    #                 coff.update({
    #                     "employee":emp.name,
    #                     "hours":coff_hours,
    #                     "comp_off_date":preday,
    #                     "validity":add_months(preday,3)
    #                 })
    #                 coff.save(ignore_permissions=True)
    #                 frappe.db.commit()
    from_date = (datetime.strptime('2019-01-25', '%Y-%m-%d')).date()
    to_date = (datetime.strptime('2019-02-24', '%Y-%m-%d')).date()
    for preday in daterange(from_date,to_date):
        employee = frappe.db.sql("""select name,employee_name,department,designation,category from `tabEmployee`
                            where status ="Active" and coff_eligible=1 """, as_dict=True)
        for emp in employee:
            #C-off for Holiday Work
            if is_holiday(emp, preday):
                ot = frappe.get_value("Attendance",{"attendance_date":preday,"employee":emp.name},["work_time"])
                if ot > (timedelta(hours = 3)):
                    calculate_ot(emp.name,preday,ot)
            #C-Off for OT
            ews = frappe.db.get_value("Employee", emp.name, ["working_shift"])
            assigned_shift = frappe.db.sql("""select shift from `tabShift Assignment`
                                where employee = %s and %s between from_date and to_date""", (emp.name, preday), as_dict=True)
            if assigned_shift:
                ews = assigned_shift[0]['shift']
            ws = frappe.get_doc("Working Shift", ews)    
            actual_in_time = ws.out_time
            actual_out_time = ws.in_time
            actual_work_hours = ws.out_time - ws.in_time
            if frappe.db.exists("Attendance", {"employee":emp.name,"attendance_date": preday}):
                attendance = frappe.get_doc("Attendance", {"employee":emp.name,"attendance_date": preday})
                if attendance.work_time > actual_work_hours:
                    ot = attendance.work_time - actual_work_hours
                    if emp.category == "Management Staff":
                        if ot > (timedelta(hours = 3)):
                            calculate_ot(emp.name,preday,ot)
                    else:
                        if ot > (timedelta(hours = 2)):
                            calculate_ot(emp.name,preday,ot)

def update_comp_off(doc,method):
    emp = doc.employee
    preday = doc.comp_off_date
    calculate_ot(emp,preday,doc.hours)

def calculate_ot(emp,preday,ot):
    ot = ot.split(":")
    ot = timedelta(hours =cint(ot[0]),minutes=cint(ot[1]))
    pre = []
    ot_time = []
    pre.append(preday)
    ot_time.append(ot)
    child = []
    emp = frappe.get_doc("Employee",emp)     
    coff_id = frappe.db.exists("Comp Off Details",{"employee":emp.name})
    if coff_id:
        coff = frappe.get_doc("Comp Off Details",coff_id)
        child = coff.comp_off_calculation_details
        comp_off_child_date = []
        comp_off_child_time = []
        for c in child:
            cdate = (c.comp_off_date).strftime('%Y-%m-%d')
            ctime = c.hours
            comp_off_child_date.append(cdate)
            comp_off_child_time.append(ctime)
        date_result = (set(comp_off_child_date) & set(pre))
        time_result = (set(comp_off_child_time) & set(ot_time))
        if (not date_result and not time_result) or (date_result and not time_result):
            child_row = coff.append("comp_off_calculation_details",{
                "comp_off_date": preday,
                "hours": ot,
                "validity": add_months(preday,3)
            }) 
    else:    
        coff = frappe.new_doc("Comp Off Details")
        coff.update({
            "employee":emp.name,
            "employee_name":emp.employee_name,
            "department":emp.department,
            "designation":emp.designation
        })
        child_row = coff.append("comp_off_calculation_details",{
            "comp_off_date": preday,
            "hours": ot,
            "validity": add_months(preday,3)
        })
        child = coff.comp_off_calculation_details
    t = timedelta(minutes = 0)
    for c in child:
        t = t + c.hours                       
    t1 = t.total_seconds()  
    minutes = t1 // 60
    hours = minutes // 60
    t3 =  "%02d:%02d:%02d" % (hours, minutes % 60, t1 % 60)
    coff.update({
        "total_hours": t3
    })
    coff.save(ignore_permissions=True)
    frappe.db.commit()

@frappe.whitelist()
def get_coff(employee):
    t_hours = 0
    if frappe.db.exists("Comp Off Details",{"employee":employee}):
        coff_hours = frappe.get_value("Comp Off Details",{"employee":employee},["total_hours"])
        # minutes = (coff_hours%3600) // 60
        return coff_hours
    else:
        return "No Data"

@frappe.whitelist()
def att_adjust(employee,attendance_date,name,in_time,out_time,status_p,status_a,status_ph,status_wo,status_first_half_present,status_second_half_present,status_first_half_absent,status_second_half_absent):
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
            if att.status == 'Present':
                att.update({
                    "status":"Present",
                    "first_half_status":"PR",
                    "admin_approved_status": "First Half Present",
                    "in_time": itime,
                    "out_time": otime
                }) 
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
            if att.status == 'Present':
                att.update({
                    "status":"Present",
                    "second_half_status":"PR",
                    "admin_approved_status": "Second Half Present",
                    "in_time": itime,
                    "out_time": otime
                }) 
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
        elif att and status_first_half_absent == "1":
            if att.status == 'Present':
                att.update({
                    "first_half_status":"AB",
                    "admin_approved_status": "First Half Absent",
                    "in_time": itime,
                    "out_time": otime
                }) 
            if att.status == 'Half Day':
                att.update({
                    "first_half_status":"AB",
                    "admin_approved_status": "First Half Absent",
                    "in_time": itime,
                    "out_time": otime
                }) 
            if att.status == 'Absent':
                att.update({
                    "first_half_status":"PR",
                    "admin_approved_status": "First Half Present",
                    "in_time": itime,
                    "out_time": otime
                })     
            att.save(ignore_permissions=True)
            frappe.db.commit()     
        elif att and status_second_half_absent == "1":
            if att.status == 'Present':
                att.update({
                    "second_half_status":"AB",
                    "admin_approved_status": "Second Half Absent",
                    "in_time": itime,
                    "out_time": otime
                }) 
            if att.status == 'Half Day':
                att.update({
                    "second_half_status":"AB",
                    "admin_approved_status": "Second Half Absent",
                    "in_time": itime,
                    "out_time": otime
                }) 
            if att.status == 'Absent':
                att.update({
                    "second_half_status":"AB",
                    "admin_approved_status": "Second Half Absent",
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
def updated_att_adjust():
    attendance = frappe.db.sql(""" select name from `tabAttendance` where docstatus =1 and attendance_date between '2019-02-26' and '2019-02-26'  """, as_dict = 1)
    for a in attendance:
        att = frappe.get_doc("Attendance",a.name)
        if att.admin_approved_status == "Present":
            att.update({
                "status":"Present"
            })
            att.save(ignore_permissions=True)
            frappe.db.commit()
        elif att.admin_approved_status == "Absent":
            att.update({
                "status":"Absent"
            })
            att.save(ignore_permissions=True)
            frappe.db.commit()
        elif att.admin_approved_status == "PH":
            att.update({
                "status":"Absent"
            })
            att.save(ignore_permissions=True)
            frappe.db.commit()
        elif att.admin_approved_status == "WO":
            att.update({
                "status":"Absent"
            })
            att.save(ignore_permissions=True)
            frappe.db.commit()
        elif att.admin_approved_status == "First Half Present":
            if att.status == 'Present':
                att.update({
                    "status":"Present",
                    "first_half_status":"PR"
                }) 
            elif att.status == 'Half Day':
                att.update({
                    "status":"Present",
                    "first_half_status":"PR"
                }) 
            elif att.status == 'Absent':
                att.update({
                    "status":"Half Day",
                    "first_half_status":"PR"
                })     
            att.save(ignore_permissions=True)
            frappe.db.commit()  
        elif att.admin_approved_status == "Second Half Present":
            if att.status == 'Present':
                att.update({
                    "status":"Present",
                    "second_half_status":"PR"
                }) 
            elif att.status == 'Half Day':
                att.update({
                    "status":"Present",
                    "second_half_status":"PR"
                }) 
            elif att.status == 'Absent':
                att.update({
                    "status":"Half Day",
                    "second_half_status":"PR"
                })     
            att.save(ignore_permissions=True)
            frappe.db.commit()     
        elif att.admin_approved_status == "First Half Absent":
            if att.status == 'Present':
                att.update({
                    "first_half_status":"AB"
                }) 
            elif att.status == 'Half Day':
                att.update({
                    "first_half_status":"AB"
                })  
            elif att.status == 'Absent':
                att.update({
                    "first_half_status":"AB"
                })     
            att.save(ignore_permissions=True)
            frappe.db.commit() 
        elif att.admin_approved_status == "Second Half Absent":
            if att.status == 'Present':
                att.update({
                    "second_half_status":"AB"
                }) 
            elif att.status == 'Half Day':
                att.update({
                    "second_half_status":"AB"
                })  
            elif att.status == 'Absent':
                att.update({
                    "second_half_status":"AB"
                })     
            att.save(ignore_permissions=True)
            frappe.db.commit()
            print att.status                
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

# @frappe.whitelist()
# def bulk_admin_att():
#     attendance = frappe.get_all("Attendance",{"admin_approved_status":("not like","")},['admin_approved_status'])
#     for att in attendance:
#         att1 = frappe.get_doc("Attendance",att)
#         att1.update({
#             "status":att['admin_approved_status']
#         })
#         att1.db_update()
#         frappe.db.commit()


@frappe.whitelist()
def fetch_att_temp():
    from_date = (datetime.strptime('2019-02-25', '%Y-%m-%d')).date()
    to_date = (datetime.strptime('2019-03-24', '%Y-%m-%d')).date()
    emp = '1208'
    for preday in daterange(from_date,to_date):
        day = preday.strftime("%d%m%Y")
        url = 'http://10.19.8.248/cosec/api.svc/v2/attendance-daily?action=get;field-name=userid,ProcessDate,firsthalf,\
                            secondhalf,punch1,punch2,workingshift,shiftstart,shiftend,latein,earlyout,worktime,overtime;date-range=%s-%s;range=user;id=1208;format=xml' % (day,day) 
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
                    print(work_time)
                    attendance_id = frappe.db.exists("Attendance", {
                        "employee": emp, "attendance_date": date_f,"docstatus":1})
                    if out_time:
                        out_time_f = datetime.strptime(out_time, "%d/%m/%Y %H:%M:%S")
                    if in_time:    
                        in_time_f = datetime.strptime(in_time, "%d/%m/%Y %H:%M:%S")
                    if in_time and out_time:
                        work_time = out_time_f - in_time_f    
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
                 

@frappe.whitelist()
def shift_assignment(employee,attendance_date,shift):
    if employee:
        shift_assignment = frappe.db.exists("Shift Assignment", {"employee": employee})
        shift = shift.split("(")
        shift = shift[0]
        if shift_assignment:
            sa = frappe.db.sql("""select name from `tabShift Assignment`
                        where employee = %s and %s between from_date and to_date """, (employee, attendance_date), as_dict=True)
            if sa:
                for s in sa:
                    doc = frappe.get_doc("Shift Assignment",s)
                    doc.update({
                        "shift":shift
                    })
                    doc.save(ignore_permissions=True)
                    frappe.db.commit()
            else:       
                doc = frappe.get_doc("Employee",employee)     
                sa = frappe.new_doc("Shift Assignment")
                sa.update({
                    "employee": employee,
                    "employee_name": doc.employee_name,
                    "business_unit": doc.business_unit,
                    "location": doc.location_name,
                    "department": doc.department,
                    "category": doc.category,
                    "from_date":attendance_date,
                    "to_date":attendance_date,
                    "shift":shift
                })
                sa.save(ignore_permissions=True)
                frappe.db.commit()
        else:       
                doc = frappe.get_doc("Employee",employee)     
                sa = frappe.new_doc("Shift Assignment")
                sa.update({
                    "employee": employee,
                    "employee_name": doc.employee_name,
                    "business_unit": doc.business_unit,
                    "location": doc.location_name,
                    "department": doc.department,
                    "category": doc.category,
                    "from_date":attendance_date,
                    "to_date":attendance_date,
                    "shift":shift
                })
                sa.save(ignore_permissions=True)
                frappe.db.commit()
    return "OK" 


@frappe.whitelist()
def update_pm_manager(doc, method):
    if doc.manager:
        pmm = frappe.db.get_value("Performance Management Manager", {
                                      "employee_code": doc.employee_code})
        if pmm:
            epmm = frappe.get_doc("Performance Management Manager", pmm)
        else:
            epmm = frappe.new_doc("Performance Management Manager")
        epmm.update({
            "employee_code": doc.employee_code,
            "employee_code1": doc.employee_code,
            "cost_code": doc.cost_code,
            "department": doc.department,
            "year_of_last_promotion": doc.year_of_last_promotion,
            "business_unit": doc.business_unit,
            "grade": doc.grade,
            "employee_name": doc.employee_name,
            "manager": doc.manager,
            "hod": doc.hod,
            "reviewer": doc.reviewer,
            "designation": doc.designation,
            "date_of_joining": doc.date_of_joining,
            "appraisal_year": doc.appraisal_year,
            "location": doc.location,
            "no_of_promotion": doc.no_of_promotion,
            "small_text_12": doc.small_text_12,
            "small_text_14": doc.small_text_14,
            "small_text_16": doc.small_text_16,
            "small_text_18": doc.small_text_18,
            "required__job_knowledge": doc.required__job_knowledge,
            "training_required_to_enhance_job_knowledge": doc.training_required_to_enhance_job_knowledge,
            "required_skills": doc.required_skills,
            "training_required__to_enhance_skills_competencies": doc.training_required__to_enhance_skills_competencies
        })
        epmm.set('sales_target', [])
        child = doc.sales_target
        for c in child:
            epmm.append("sales_target",{
                "year": c.year,
                "actual_targets": c.actual_targets,
                "attained_targets": c.attained_targets
            })
        epmm.set('job_analysis', [])
        child1 = doc.job_analysis
        for c in child1:
            epmm.append("job_analysis",{
                "appraisee_remarks": c.appraisee_remarks
            })
        epmm.set('competency_assessment1', [])
        child2 = doc.competency_assessment1
        for c in child2:
            epmm.append("competency_assessment1",{
                "competency": c.competency,
                "weightage": c.weightage,
                "appraisee_weightage": c.appraisee_weightage,
                "manager": c.appraisee_weightage
            })
        epmm.set('key_result_area', [])
        child3 = doc.key_result_area
        for c in child3:
            epmm.append("key_result_area",{
                "goal_setting_for_current_year": c.goal_setting_for_current_year,
                "performance_measure": c.performance_measure,
                "weightage_w_100": c.weightage_w_100,
                "self_rating": c.self_rating,
                "manager": c.self_rating,
                "weightage": c.weightage,
            })
        epmm.set('key_results_area', [])
        child4 = doc.key_results_area
        for c in child4:
            epmm.append("key_results_area",{
                "goal_setting_for_last_year": c.goal_setting_for_last_year,
                "performance_measure": c.performance_measure,
                "weightage_w_100": c.weightage_w_100,
                "self_rating": c.self_rating,
                "weightage": c.weightage,
            })
        epmm.save(ignore_permissions=True)
    else:
        pmm = frappe.db.get_value("Performance Management HOD", {
                                      "employee_code": doc.employee_code})
        if pmm:
            epmm = frappe.get_doc("Performance Management HOD", pmm)
        else:
            epmm = frappe.new_doc("Performance Management HOD")
        epmm.update({
            "employee_code": doc.employee_code,
            "employee_code1": doc.employee_code,
            "cost_code": doc.cost_code,
            "department": doc.department,
            "year_of_last_promotion": doc.year_of_last_promotion,
            "business_unit": doc.business_unit,
            "grade": doc.grade,
            "employee_name": doc.employee_name,
            "manager": doc.manager,
            "hod": doc.hod,
            "reviewer": doc.reviewer,
            "designation": doc.designation,
            "date_of_joining": doc.date_of_joining,
            "appraisal_year": doc.appraisal_year,
            "location": doc.location,
            "no_of_promotion": doc.no_of_promotion,
            "small_text_12": doc.small_text_12,
            "small_text_14": doc.small_text_14,
            "small_text_16": doc.small_text_16,
            "small_text_18": doc.small_text_18,
            "potential": "NA",
            "performance": "NA",
            "promotion": "NA",
            "any_other_observations": "NA",
            "required__job_knowledge": doc.required__job_knowledge,
            "training_required_to_enhance_job_knowledge": doc.training_required_to_enhance_job_knowledge,
            "required_skills": doc.required_skills,
            "training_required__to_enhance_skills_competencies": doc.training_required__to_enhance_skills_competencies
        })
        epmm.set('sales_target', [])
        child = doc.sales_target
        for c in child:
            epmm.append("sales_target",{
                "year": c.year,
                "actual_targets": c.actual_targets,
                "attained_targets": c.attained_targets
            })
        epmm.set('job_analysis', [])
        child1 = doc.job_analysis
        for c in child1:
            epmm.append("job_analysis",{
                "appraisee_remarks": c.appraisee_remarks,
                "appraiser_remarks": "NA"
            })
        epmm.set('competency_assessment1', [])
        child2 = doc.competency_assessment1
        for c in child2:
            epmm.append("competency_assessment1",{
                "competency": c.competency,
                "weightage": c.weightage,
                "appraisee_weightage": c.appraisee_weightage,
                "manager": "NA",
                "hod": c.appraisee_weightage
            })
        epmm.set('key_result_area', [])
        child3 = doc.key_result_area
        for c in child3:
            epmm.append("key_result_area",{
                "goal_setting_for_current_year": c.goal_setting_for_current_year,
                "performance_measure": c.performance_measure,
                "weightage_w_100": c.weightage_w_100,
                "self_rating": c.self_rating,
                "weightage": c.weightage,
                "manager": "NA",
                "hod": c.self_rating
            })
        epmm.set('key_results_area', [])
        child4 = doc.key_results_area
        for c in child4:
            epmm.append("key_results_area",{
                "goal_setting_for_last_year": c.goal_setting_for_last_year,
                "performance_measure": c.performance_measure,
                "weightage_w_100": c.weightage_w_100,
                "weightage": c.weightage,
                "self_rating": c.self_rating
            })
        epmm.set('employee_feedback', [])
        # child5 = doc.employee_feedback
        for c in range(5):
            epmm.append("employee_feedback",{
                "appraisee_remarks": "NA"
            })
        epmm.save(ignore_permissions=True)



@frappe.whitelist()
def update_pm_hod(doc, method):
    if doc.manager == frappe.session.user:
        pmm = frappe.db.get_value("Performance Management HOD", {
                                      "employee_code": doc.employee_code})
        if pmm:
            epmm = frappe.get_doc("Performance Management HOD", pmm)
        else:
            epmm = frappe.new_doc("Performance Management HOD")
        epmm.update({
            "employee_code": doc.employee_code,
            "employee_code1": doc.employee_code,
            "cost_code": doc.cost_code,
            "department": doc.department,
            "year_of_last_promotion": doc.year_of_last_promotion,
            "business_unit": doc.business_unit,
            "grade": doc.grade,
            "employee_name": doc.employee_name,
            "manager": doc.manager,
            "hod": doc.hod,
            "reviewer": doc.reviewer,
            "designation": doc.designation,
            "date_of_joining": doc.date_of_joining,
            "appraisal_year": doc.appraisal_year,
            "location": doc.location,
            "no_of_promotion": doc.no_of_promotion,
            "small_text_12": doc.small_text_12,
            "small_text_14": doc.small_text_14,
            "small_text_16": doc.small_text_16,
            "small_text_18": doc.small_text_18,
            "potential": doc.potential,
            "performance": doc.performance,
            "promotion": doc.promotion,
            "any_other_observations": doc.any_other_observations,
            "required__job_knowledge": doc.required__job_knowledge,
            "training_required_to_enhance_job_knowledge": doc.training_required_to_enhance_job_knowledge,
            "required_skills": doc.required_skills,
            "training_required__to_enhance_skills_competencies": doc.training_required__to_enhance_skills_competencies
        })
        epmm.set('sales_target', [])
        child = doc.sales_target
        for c in child:
            epmm.append("sales_target",{
                "year": c.year,
                "actual_targets": c.actual_targets,
                "attained_targets": c.attained_targets
            })
        epmm.set('job_analysis', [])
        child1 = doc.job_analysis
        for c in child1:
            epmm.append("job_analysis",{
                "appraisee_remarks": c.appraisee_remarks,
                "appraiser_remarks": c.appraiser_remarks
            })
        epmm.set('competency_assessment1', [])
        child2 = doc.competency_assessment1
        for c in child2:
            epmm.append("competency_assessment1",{
                "competency": c.competency,
                "weightage": c.weightage,
                "appraisee_weightage": c.appraisee_weightage,
                "manager": c.manager,
                "hod": c.manager
            })
        epmm.set('key_result_area', [])
        child3 = doc.key_result_area
        for c in child3:
            epmm.append("key_result_area",{
                "goal_setting_for_current_year": c.goal_setting_for_current_year,
                "performance_measure": c.performance_measure,
                "weightage_w_100": c.weightage_w_100,
                "self_rating": c.self_rating,
                "weightage": c.weightage,
                "manager": c.manager,
                "hod": c.manager
            })
        epmm.set('key_results_area', [])
        child4 = doc.key_results_area
        for c in child4:
            epmm.append("key_results_area",{
                "goal_setting_for_last_year": c.goal_setting_for_last_year,
                "performance_measure": c.performance_measure,
                "weightage_w_100": c.weightage_w_100,
                "weightage": c.weightage,
                "self_rating": c.self_rating
            })
        epmm.set('employee_feedback', [])
        child5 = doc.employee_feedback
        for c in child5:
            epmm.append("employee_feedback",{
                "appraisee_remarks": c.appraisee_remarks
            })
        epmm.save(ignore_permissions=True)
        



@frappe.whitelist()
def update_pm_reviewer(doc, method):
    if doc.hod == frappe.session.user:
        pmm = frappe.db.get_value("Performance Management Reviewer", {
                                      "employee_code": doc.employee_code})
        if pmm:
            epmm = frappe.get_doc("Performance Management Reviewer", pmm)
        else:
            epmm = frappe.new_doc("Performance Management Reviewer")
        epmm.update({
            "employee_code": doc.employee_code,
            "employee_code1": doc.employee_code,
            "cost_code": doc.cost_code,
            "department": doc.department,
            "year_of_last_promotion": doc.year_of_last_promotion,
            "business_unit": doc.business_unit,
            "grade": doc.grade,
            "employee_name": doc.employee_name,
            "manager": doc.manager,
            "hod": doc.hod,
            "reviewer": doc.reviewer,
            "designation": doc.designation,
            "date_of_joining": doc.date_of_joining,
            "appraisal_year": doc.appraisal_year,
            "location": doc.location,
            "no_of_promotion": doc.no_of_promotion,
            "small_text_12": doc.small_text_12,
            "small_text_14": doc.small_text_14,
            "small_text_16": doc.small_text_16,
            "small_text_18": doc.small_text_18,
            "potential": doc.potential,
            "performance": doc.performance,
            "promotion": doc.promotion,
            "any_other_observations": doc.any_other_observations,
            "potential_hod": doc.potential_hod,
            "performance_hod": doc.performance_hod,
            "promotion_hod": doc.promotion_hod,
            "any_other_observations_hod": doc.any_other_observations_hod,
            "required__job_knowledge": doc.required__job_knowledge,
            "training_required_to_enhance_job_knowledge": doc.training_required_to_enhance_job_knowledge,
            "required_skills": doc.required_skills,
            "training_required__to_enhance_skills_competencies": doc.training_required__to_enhance_skills_competencies
        })
        epmm.set('sales_target', [])
        child = doc.sales_target
        for c in child:
            epmm.append("sales_target",{
                "year": c.year,
                "actual_targets": c.actual_targets,
                "attained_targets": c.attained_targets
            })
        epmm.set('job_analysis', [])
        child1 = doc.job_analysis
        for c in child1:
            epmm.append("job_analysis",{
                "appraisee_remarks": c.appraisee_remarks,
                "appraiser_remarks": c.appraiser_remarks
            })
        epmm.set('competency_assessment1', [])
        child2 = doc.competency_assessment1
        for c in child2:
            epmm.append("competency_assessment1",{
                "competency": c.competency,
                "weightage": c.weightage,
                "appraisee_weightage": c.appraisee_weightage,
                "appraiser_rating": c.manager,
                "hod": c.hod,
                "reviewer": c.hod
            })
        epmm.set('key_result_area', [])
        child3 = doc.key_result_area
        for c in child3:
            epmm.append("key_result_area",{
                "goal_setting_for_current_year": c.goal_setting_for_current_year,
                "performance_measure": c.performance_measure,
                "weightage_w_100": c.weightage_w_100,
                "weightage": c.weightage,
                "self_rating": c.self_rating,
                "appraiser_rating_r": c.manager,
                "hod": c.hod,
                "reviewer": c.hod
            })
        epmm.set('key_results_area', [])
        child4 = doc.key_results_area
        for c in child4:
            epmm.append("key_results_area",{
                "goal_setting_for_last_year": c.goal_setting_for_last_year,
                "performance_measure": c.performance_measure,
                "weightage_w_100": c.weightage_w_100,
            })
        epmm.set('employee_feedback', [])
        child5 = doc.employee_feedback
        for c in child5:
            epmm.append("employee_feedback",{
                "appraisee_remarks": c.appraisee_remarks,
                "hod": c.hod
            })
        # epmm.set('pm_observation_feedback', [])
        # child5 = doc.pm_observation_feedback
        # for c in child5:
        #     epmm.append("pm_observation_feedback",{
        #         "appraiser_reviewer": c.appraiser_reviewer,
        #         "status": c.status
        #     })
        epmm.save(ignore_permissions=True)


        
@frappe.whitelist()
def send_announcement(name):
    doc = frappe.get_doc('Employee', name)
    experience = doc.external_work_history
    edu = doc.education
    if doc.one_above_manager:
        report_manager_doc = frappe.get_doc('Employee', {"user_id": doc.one_above_manager})
    else:
        report_manager_doc = " "
    for i in range(1):
        frappe.errprint("hi")
        content = """
        <h1><br></h1>
        <h1 align="center"><u><span style="font-size: 14px;">&nbsp;</span></u></h1>
        <h1 align="center"><br><u><span style="font-size: 14px;"></span></u></h1>
        <h1 align="center"><u><span style="font-size: 14px;">ORGANIZATIONAL ANNOUNCE</span></u><span style="font-size: 14px;">﻿</span><u><span style="font-size: 14px;">MENT</span></u><span style="font-size: 14px;"></span><span style="font-size: 14px;"></span></h1>
        <center><div><span style="font-size: 12px;">HDI/HR&amp;ADM/QA-150</span></div></center>
        <center><div><span style="font-size: 12px;">February 22,2019</span></div></center>
        <div align="left"><span style="font-size: 12px;"><br></span></div>
        <div align="left"><span style="font-size: 12px;"><br></span></div>
        <div align="left"><span style="font-size: 14px;">I&nbsp; have great pleasure in Welcoming&nbsp;<b> %s . %s</b>, who has joined in our organization on <b>%s</b> as <b>%s</b> based out of <b>%s</b>.</span></div>
        <div align="left"><span style="font-size: 12px;"><br></span></div>
        <div align="left"><span style="font-size: 12px;"><br></span></div>
        <div align="left"><span style="font-size: 14px;">Before joinnig HDI, he was working as<b> %s </b>with<b> %s</b>.&nbsp; <b>%s</b> has completed&nbsp;<b> %s</b> and he shall Report to <b>%s . %s, %s.</b></span></div>
        <div align="left"><span style="font-size: 12px;"><br></span></div>
        <div align="left"><span style="font-size: 14px;"><br></span></div>
        <div align="left"><span style="font-size: 14px;">Email </span><a><span style="font-size: 14px;">ID:<u>%s</u></span></a></div>
        <div align="left"><span style="font-size: 12px;"><br></span></div>
        <div align="left"><span style="font-size: 12px;"><br></span></div>
        <div align="left"><span style="font-size: 14px;">I extend him warm welcome to our Hunter Douglas India Family and sure that all of you will add on the same.</span></div>
        <div align="left"><span style="font-size: 12px;"><br></span></div>
        <div align="left"><span style="font-size: 12px;"><br></span></div>
        <div align="left"><b><span style="font-size: 14px;">Best Wishes,</span></b></div>
        <div align="left"><b><span style="font-size: 12px;"><br></span></b></div>
        <div align="left"><b><span style="font-size: 12px;"><br></span></b></div>
        <div align="left"><b><span style="font-size: 12px;"><br></span></b></div>
        <div align="left"><b><span style="font-size: 14px;">(S.Raghavan)</span></b></div>
        <div align="left"><b><span style="font-size: 12px;"><span style="font-size: 14px;"> Financial Controller</span><br></span></b></div>
        <div align="left"><span style="font-size: 12px;"><br></span></div>
        </center><center><div><br></div>
        <div><br></div>
        </center> 
        """ %(doc.salutation,doc.employee_name,doc.date_of_joining,doc.designation,doc.location_name,experience[0].designation,
        experience[0].company_name,doc.employee_name,edu[0].qualification,report_manager_doc.salutation,report_manager_doc.employee_name,report_manager_doc.designation,doc.user_id)
        frappe.sendmail(
            recipients=['ramya.a@voltechgroup.com'],
            subject='Announcement For All',
            message=""" %s""" % (content))
    # return content



@frappe.whitelist()
def update_hod():
    self_list = ["PMS0076"]
    for s in self_list:
        doc = frappe.get_doc("Performance Management Self", s)
        if doc.docstatus == 1 and doc.manager:
            pmm = frappe.db.get_value("Performance Management Manager", {
                                        "employee_code": doc.employee_code})
            if pmm:
                epmm = frappe.get_doc("Performance Management Manager", pmm)
            else:
                epmm = frappe.new_doc("Performance Management Manager")
            epmm.update({
                "employee_code": doc.employee_code,
                "cost_code": doc.cost_code,
                "department": doc.department,
                "year_of_last_promotion": doc.year_of_last_promotion,
                "business_unit": doc.business_unit,
                "grade": doc.grade,
                "employee_name": doc.employee_name,
                "manager": doc.manager,
                "hod": doc.hod,
                "reviewer": doc.reviewer,
                "designation": doc.designation,
                "date_of_joining": doc.date_of_joining,
                "appraisal_year": doc.appraisal_year,
                "location": doc.location,
                "no_of_promotion": doc.no_of_promotion,
                "small_text_12": doc.small_text_12,
                "small_text_14": doc.small_text_14,
                "small_text_16": doc.small_text_16,
                "small_text_18": doc.small_text_18,
                # "potential": "NA",
                # "performance": "NA",
                # "promotion": "NA",
                # "any_other_observations": "NA",
                "required__job_knowledge": doc.required__job_knowledge,
                "training_required_to_enhance_job_knowledge": doc.training_required_to_enhance_job_knowledge,
                "required_skills": doc.required_skills,
                "training_required__to_enhance_skills_competencies": doc.training_required__to_enhance_skills_competencies
            })
            epmm.set('sales_target', [])
            child = doc.sales_target
            for c in child:
                epmm.append("sales_target",{
                    "year": c.year,
                    "actual_targets": c.actual_targets,
                    "attained_targets": c.attained_targets
                })
            epmm.set('job_analysis', [])
            child1 = doc.job_analysis
            for c in child1:
                epmm.append("job_analysis",{
                    "appraisee_remarks": c.appraisee_remarks,
                    # "appraiser_remarks": "NA"
                })
            epmm.set('competency_assessment1', [])
            child2 = doc.competency_assessment1
            for c in child2:
                epmm.append("competency_assessment1",{
                    "competency": c.competency,
                    "weightage": c.weightage,
                    "appraisee_weightage": c.appraisee_weightage,
                    # "manager": "NA",
                    # "hod": c.appraisee_weightage
                })
            epmm.set('key_result_area', [])
            child3 = doc.key_result_area
            for c in child3:
                epmm.append("key_result_area",{
                    "goal_setting_for_current_year": c.goal_setting_for_current_year,
                    "performance_measure": c.performance_measure,
                    "weightage_w_100": c.weightage_w_100,
                    "self_rating": c.self_rating,
                    "weightage": c.weightage,
                    # "manager": "NA",
                    # "hod": c.self_rating
                })
            epmm.set('key_results_area', [])
            child4 = doc.key_results_area
            for c in child4:
                epmm.append("key_results_area",{
                    "goal_setting_for_last_year": c.goal_setting_for_last_year,
                    "performance_measure": c.performance_measure,
                    "weightage_w_100": c.weightage_w_100,
                    "weightage": c.weightage,
                    "self_rating": c.self_rating
                })
            # epmm.set('employee_feedback', [])
            # # child5 = doc.employee_feedback
            # for c in range(5):
            #     epmm.append("employee_feedback",{
            #         "appraisee_remarks": "NA"
            #     })
            epmm.save(ignore_permissions=True)
            frappe.db.commit()


# @frappe.whitelist()
# def submit_leave_application():
#     leave = frappe.get_all("Leave Application",{"docstatus":0, "status": "Approved"},['name'])
#     for l in leave:
#         doc = frappe.get_doc("Leave Application",l)
#         frappe.errprint(doc.status)
        # doc.save(ignore_permissions=True)
        # doc.submit()

# def get_mr_in(doc,method):
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


@frappe.whitelist()
def check_attendance_status(employee,from_date,to_date):
    query = """select name,employee,attendance_date,status from `tabAttendance` where employee=%s and attendance_date between '%s' and '%s' """ % (employee,from_date,to_date)
    attendance = frappe.db.sql(query,as_dict=True)
    for a in attendance:
        doc = frappe.get_doc("Attendance",a.name)
        doc.update({
            "status": "Absent"
        })
        doc.save(ignore_permissions=True)
        doc.submit()
        frappe.db.commit()
        frappe.errprint(doc.status)
        return "Ok"

@frappe.whitelist()
def update_ecode():
    pmm = frappe.get_all("Performance Management Reviewer",fields=['name','employee_code'])
    for pm in pmm:
        # print loop.index
        print pm['name']
        frappe.db.set_value("Performance Management Reviewer",pm['name'],"employee_code1",pm['employee_code'])
        frappe.db.commit()