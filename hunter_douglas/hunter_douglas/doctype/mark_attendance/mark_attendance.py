# -*- coding: utf-8 -*-
# Copyright (c) 2020, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from datetime import datetime,timedelta
import time
from frappe.model.document import Document

class MarkAttendance(Document):
    pass
@frappe.whitelist()
def create_self_attendance(employee_id,employee_name,in_time,attendance_date):
    # c_time = datetime.strptime(str(in_time), '%Y-%m-%d %H:%M:%S').time()
    att_time = datetime.strptime(str(in_time), '%H:%M:%S')
    frappe.errprint(type(att_time))
    frappe.errprint(att_time)
    a = att_time.time()
    frappe.errprint(a)
    fulldate = a + datetime.timedelta(hours=8)
    frappe.errprint(fulldate)
    # my_time   = time.localtime()
    # time.strftime(in_time.encode('utf-8'), my_time).decode('utf-8')
    # frappe.errprint(my_time)
    # out=my_time + timedelta(5)
    # date = datetime.datetime.now().strftime(“%y%m%d_%h%m%s “)
    # out_time = datetime.strptime('08:00', '%H:%M')
    # frappe.errprint(type(out_time))
    # frappe.errprint(out_time)
    # b = out_time.time()
    # frappe.errprint(b)
    # new_time = (a - b).total_seconds()/3600
    # new_time = s = datetime.timedelta(a) + datetime.timedelta(b)
    # frappe.errprint(new_time)
    # out_time = datetime.strptime(str(a), '%H:%M:%S')
    # frappe.errprint(type(out_time))
    # frappe.errprint(out_time)
    # out = att_time + out_time
    # frappe.errprint(out)
    sa=frappe.new_doc("Attendance")
    sa.employee=employee_id
    sa.employee_name=employee_name
    sa.attendance_date=attendance_date
    sa.in_time=in_time
    sa.is_self_attendance = 1
    sa.status = "Present"
    # sa.out_time=eight_hours
    sa.save(ignore_permissions=True)
    frappe.db.commit()
    return sa