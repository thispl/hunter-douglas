# Copyright (c) 2013, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import math
import json
from calendar import monthrange
from datetime import datetime,timedelta,date
from dateutil.rrule import * 
from frappe.utils import today,getdate, cint, add_months, date_diff, add_days, nowdate, \
    get_datetime_str, cstr, get_datetime, time_diff, time_diff_in_seconds
# from hunter_douglas.hunter_douglas.report.monthly_absenteesim.monthly_absenteesim import validate_if_attendance_not_applicable    

@frappe.whitelist()
def update_attendance(data, name):
    frappe.errprint(date)
    dictionary = convert_string_to_dict(data)
    
    # Update session1 value
    if "session1" in dictionary:
        session1 = dictionary["session1"]
        if session1 == "AB":
            con = json.dumps(data)
            value = '<a onclick="frappe.query_reports[\'Attendance recapitulation\'].open_att_adjust1(' + con + ')"><span style="color:red!important;font-weight:bold">' + value + '</a></span>'
        elif session1 == "PR" or session1 == "CL":
            value = "<span style='color:green!important;font-weight:bold'>" + value + "</span>"
    
    # Update session2 value
    if "session2" in dictionary:
        session2 = dictionary["session2"]
        if session2 == "AB":
            con = json.dumps(data)
            value = '<a onclick="frappe.query_reports[\'Attendance recapitulation\'].open_att_adjust1(' + con + ')"><span style="color:red!important;font-weight:bold">' + value + "</a></span>"
        elif session2 == "PR":
            value = "<span style='color:green!important;font-weight:bold'>" + value + "</span>"
        elif session2 == "CL" or session2 == "PL" or session2 == "SL":
            value = "<span style='color:blue!important;font-weight:bold'>" + value + "</span>"
    
    for i in dictionary.values():
        if i == 1:
            value = 1
            keys = get_keys_of_values(dictionary, value)
            frappe.errprint(keys)
            if keys == ["present"] or keys == ["absent"]:
                att = frappe.get_doc('Attendance', name)
                
                if keys == ["present"]:
                    att.status = "Present"
                if keys == ["absent"]:
                    att.status = "Absent"
                att.save(ignore_permissions=True)
                frappe.msgprint("Attendance Updated Successfully")
    
    return value




@frappe.whitelist()
def update_attendance(data,name):
    frappe.errprint(date)
    dictionary = convert_string_to_dict(data)
    for i in dictionary.values():
        if i == 1:
            value = 1
            keys = get_keys_of_values(dictionary, value)
            frappe.errprint(keys)
            if keys == ["present"] or keys == ["absent"]:
                att = frappe.get_doc('Attendance', name)
                
                if keys == ["present"]:
                    att.status = "Present"
                if keys == ["absent"]:
                    att.status = "Absent"
                att.save(ignore_permissions = True)
                
                frappe.msgprint("Attendance Updated Successfully")
                return att.status
                



            at = frappe.get_doc('Attendance', name)
            if keys == ["cl"] or keys == ["pl"] or keys == ["sl"] or keys == ["el"]:
                l = frappe.new_doc("Leave Application")
                l.employee = at.employee
                l.from_date = at.attendance_date
                l.to_date = at.attendance_date
                if keys == ["cl"]:
                    l.leave_type1 = "Casual Leave"
                    l.leave_type = "Casual Leave"
                
                if keys == ["sl"]:
                    l.leave_type1 = "Sick Leave"
                    l.leave_type = "Sick Leave"

                if keys == ["pl"]:
                    l.leave_type1 = "Privilege Leave"
                    l.leave_type = "Privilege Leave"

                l.reason = "Test"
                l.status = "Applied"
                lp = frappe.get_value("Employee",{"employee_number":at.employee},["hod"])
                l.leave_approver = lp
                l.save(ignore_permissions = True)
                frappe.msgprint("Leave Application Created")

def convert_string_to_dict(data):
  """Converts a string into a dictionary using the `json.loads()` function."""
  dictionary = json.loads(data)
  return dictionary

def get_keys_of_values(dictionary, value):
  """Gets the keys of the values in the dictionary."""
  keys = [key for key, val in dictionary.items() if val == value]
  return keys
