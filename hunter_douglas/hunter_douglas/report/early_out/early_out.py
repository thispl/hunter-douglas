# Copyright (c) 2013, teampro and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from six import string_types
import frappe
from datetime import datetime
from frappe.utils import (getdate, cint, add_months, date_diff, add_days,
	nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime,format_date)
from calendar import monthrange
from frappe import _, msgprint
from frappe.utils import flt
from frappe.utils import cstr, cint, getdate
from itertools import count
import pandas as pd
import datetime as dt


def execute(filters=None):
	data = []
	columns = get_columns()
	attendance = get_attendance(filters)
	for att in attendance:
		data.append(att)
	return columns, data

def get_columns():
	columns = [
		_("Employee") + ":Data:120",
		_("Employee Name") + ":Data:120",
		_("Department") + ":Data:120",
		_("Attendance Date") + ":Data:120",
		_("Shift") + ":Data:120",
		_("Shift End Time") + ":Data:100",
		_("Out Time") + ":Data:120",
		_("Early Out Hours") + ":Data:100"
	]
	return columns

def get_attendance(filters):
	data = []
	# if filters.employee:
	#     attendance = frappe.get_all('Attendance',{'status':'Present','attendance_date':('between',(filters.from_date,filters.to_date)),'employee':filters.employee},['*'])
	#     for att in attendance:
	#         if att.working_shift and att.out_time:
	#             shift_time = frappe.get_value("Working Shift",{'name':att.working_shift},["out_time"])
	#             get_time = datetime.strptime(str(shift_time),'%H:%M:%S').strftime('%H:%M:%S')
	#             shift_end_time = dt.datetime.strptime(str(get_time),'%Y-%m-%d %H:%M:%S')
	#             out_time = dt.datetime.combine(att.attendance_date,shift_end_time.time())
	#             st_time = out_time.strftime('%Y-%m-%d %H:%M:%S')
	#             at_time = att.out_time.strftime('%Y-%m-%d %H:%M:%S')
	#             if att.out_time < out_time:
	#                         early_time = out_time - att.out_time
	#                         row = [att.employee,att.employee_name,att.department,format_date(att.attendance_date),att.working_shift,st_time,at_time,early_time]
	#                         data.append(row)
	# elif filters.department:
	#     attendance = frappe.get_all('Attendance',{'status':'Present','attendance_date':('between',(filters.from_date,filters.to_date)),'department':filters.department},['*'])
	#     for att in attendance:
	#         if att.shift and att.out_time:
	#             shift_time = frappe.get_value("Working Shift",{'name':att.shift},["out_time"])
	#             get_time = datetime.strptime(str(shift_time),'%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
	#             shift_end_time = dt.datetime.strptime(str(get_time),'%Y-%m-%d %H:%M:%S')
	#             out_time = dt.datetime.combine(att.attendance_date,shift_end_time.time())
	#             st_time = out_time.strftime('%Y-%m-%d %H:%M:%S')
	#             at_time = att.out_time.strftime('%Y-%m-%d %H:%M:%S')
	#             if att.out_time < out_time:
	#                         early_time = out_time - att.out_time
	#                         row = [att.employee,att.employee_name,att.department,format_date(att.attendance_date),att.working_shift,st_time,at_time,early_time]
	#                         data.append(row)
	# else:
	# attendance = frappe.get_all('Attendance',{'attendance_date':('between',(filters.from_date,filters.to_date))},['*'])
	# late_by = ''
	# for att in attendance:
	#     if att.shift and att.out_time:
	#         shift_end_time = frappe.db.get_value("Shift Type",att.shift,"end_time")
	#         shift_end = pd.to_datetime(str(shift_end_time)).time()
	#         out_time = dt.datetime.strptime(att.out_time,'%Y-%m-%d %H:%M:%S')
	#         if out_time.time() < shift_end:
	#             dt.datetime_combine = datetime.combine(att.attendance_date,shift_end)
	#             total_hours = dt.datetime_combine - att.out_time
	#             row = [att.employee,att.employee_name,format_date(att.attendance_date),att.shift,shift_end_time,att.out_time,total_hours]
	#             data.append(row)
	# return data


	attendance = frappe.get_all('Attendance',{'attendance_date':('between',(filters.from_date,filters.to_date))},['*'])
	for att in attendance:
		if att.shift and att.out_time:
			out_time = dt.datetime.strptime(str(att.out_time),'%Y-%m-%d %H:%M:%S')
			shift_time = frappe.get_value("Shift Type",{'name':att.shift},["end_time"])
			get_time = datetime.strptime(str(shift_ti M+ me),'%H:%M:%S').strftime('%H:%M:%S')
			shift_end_time = dt.datetime.strptime(str(get_time),"%H:%M:%S")
			end_time = dt.datetime.combine(att.attendance_date,shift_end_time.time())
			st_time = end_time.strftime('%H:%M')
			at_time = out_time.strftime('%H:%M')
			if out_time < end_time:
				early_time = end_time - out_time

				row = [att.employee,att.employee_name,att.department,format_date(att.attendance_date),att.shift,
				st_time,at_time,early_time]
				data.append(row)
	return data