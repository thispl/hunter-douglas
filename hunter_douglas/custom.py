# -*- coding: utf-8 -*-
# Copyright (c) 2017, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import requests
import json
from datetime import datetime,timedelta
from frappe.utils import today,flt
from frappe import _
import xml.etree.ElementTree as ET



@frappe.whitelist()
def fetch_att():
    day = datetime.today().strftime("%d%m%Y")
    date = datetime.today().strftime("%Y-%m-%d")
    # url = 'http://182.72.89.102/cosec/api.svc/attendance-daily?action=get;date-range=%s-%s;range=all;format=xml' % (day,day) 
    url = 'http://182.72.89.102/cosec/api.svc/attendance-daily?action=get;date-range=01012018-17102018;range=all;format=xml'
    r = requests.get(url, auth=('sa', 'matrixx'))
    root = ET.fromstring(r.content)
    for att in root.findall('attendance-daily'):
        userid = att.find('UserID').text
        in_time = att.find('Punch1').text
        out_time = att.find('Punch2').text
        date = datetime.strptime((att.find('ProcessDate').text.replace("/","")), "%d%m%Y").date()
        date_f = date.strftime("%Y-%m-%d")
        work_time = timedelta(minutes=flt(att.find('WorkTime').text))
        employee = frappe.db.get_value("Employee", {
        "employee_number": userid, "status": "Active"})
        if employee:
            attendance_id = frappe.db.get_value("Attendance", {
                "employee": employee, "attendance_date": date_f})
            if attendance_id:
                attendance = frappe.get_doc(
                    "Attendance", attendance_id)
                attendance.out_time = out_time
                attendance.in_time = in_time
                attendance.work_time = work_time
                attendance.db_update()
                frappe.db.commit()
            else:
                attendance = frappe.new_doc("Attendance")
                in_time = in_time
                attendance.update({
                    "employee": employee,
                    "attendance_date": date_f,
                    "status": "Present",
                    # "shift": shift,
                    "in_time": in_time,
                    "out_time": out_time,
                    "work_time": work_time
                })
                attendance.save(ignore_permissions=True)
                attendance.submit()
                frappe.db.commit()