# Copyright (c) 2013, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import datetime

def execute(filters=None):
    if not filters:
        filters = {}
    data = row = []
    filters["month"] = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
		"Dec"].index(filters.month) + 1
    
    columns = [_("Shift") + ":Data:100"] 

    days = range(25,32) + range(1,25)
    for day in days:
        columns += [(_(day) + ":Int:80") ]
        
    for shift in frappe.get_list('Working Shift',fields=['name']):
        row = [shift['name']]
        for day in days:
            if day in range(25,32):
                day_f = str(filters.year) +'-'+str(filters.month - 1)+'-'+str(day)
            else:
                day_f = str(filters.year) +'-'+str(filters.month)+'-'+str(day)    
            att = frappe.db.sql(
                        """select count(att.status) as `count` from `tabAttendance` att where att.status='Present' and 
                            att.attendance_date='%s' and att.working_shift='%s'""" % (day_f,shift['name']) ,as_dict=1)
            for at in att:
                att_count = at.count
            row += [att_count]     
        data.append(row)
    return columns, data
