from os import name
import frappe
from numpy import empty
import pandas as pd
import json
import datetime
from frappe.permissions import check_admin_or_system_manager
from frappe.utils.csvutils import read_csv_content
from six.moves import range
from six import string_types
from frappe.utils import (getdate, cint, add_months, date_diff, add_days,
	nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime)
from datetime import datetime
from calendar import monthrange
from frappe import _, msgprint
from frappe.utils import flt
from frappe.utils import cstr, cint, getdate,get_first_day, get_last_day, today, time_diff_in_hours
import requests

from datetime import date, timedelta,time
from frappe.utils.background_jobs import enqueue
from frappe.utils import get_url_to_form
import math

frappe.whitelist()
def mark_att(from_date,to_date):
	# from_date= "2023-11-23"
	# to_date = "2023-12-19"

	from_date= get_first_day(today())
	to_date = today()
	
	employee_checkins = frappe.db.sql("""select * from `tabEmployee Checkin` where  date(time) between '%s' and '%s' order by time """%(from_date,to_date),as_dict=True) 
   
	if employee_checkins:
		date = employee_checkins[0].time
		from_date = datetime.strftime(date,'%Y-%m-%d')
		
		for c in employee_checkins:
			mark_attendance_from_checkin(c.employee,c.time,c.device_id)

def mark_attendance_from_checkin(employee,time,device):
	att_time = time.time()
	att_date = time.date()
	in_time = ''
	out_time = ''
	checkins = frappe.db.sql(""" select name,time from `tabEmployee Checkin` where employee = '%s' and date(time)  = '%s' order by time """%(employee,att_date),as_dict=True)
	
	if checkins:
		if device in ['Silvasa']:
			if datetime.strptime('04:30:00','%H:%M:%S').time() < att_time < datetime.strptime('08:15:00','%H:%M:%S').time():
				if len(checkins) >= 2:
					in_time = checkins[0].time
					out_time = checkins[-1].time
				elif len(checkins) == 1:
					in_time = checkins[0].time
					out_time = checkins[-1].time
				attn = frappe.db.exists('Attendance',{'employee':employee,'attendance_date':att_date,'docstatus':0})
				print(attn)
				status = ""
				if in_time and out_time:
					if in_time == out_time:
						status = 'Absent'
					elif in_time != out_time:	
						status = 'Present'
				else:
					status = 'Absent'
				if not attn:
					att = frappe.new_doc('Attendance')
					att.employee = employee
					att.attendance_date = att_date
					att.status = status
					att.in_time = in_time
					att.out_time = out_time
					att.save(ignore_permissions=True)
					frappe.db.commit()
				else:
					if in_time:
						frappe.db.set_value('Attendance',attn,'in_time',in_time)
					if out_time:
						frappe.db.set_value('Attendance',attn,'out_time',out_time)

					frappe.db.set_value("Attendance",attn,'status',status)
				for c in checkins:
					print(c)
					frappe.db.set_value("Employee Checkin",c.name,"skip_auto_attendance",'1')
					frappe.db.set_value("Employee Checkin",c.name,"attendance",attn)
				
			elif datetime.strptime('08:15:00','%H:%M:%S').time() < att_time < datetime.strptime('12:15:00','%H:%M:%S').time():
				
				if len(checkins) >= 2:
					in_time = checkins[0].time
					out_time = checkins[-1].time
				elif len(checkins) == 1:
					in_time = checkins[0].time
					out_time = checkins[-1].time
				attn = frappe.db.exists('Attendance',{'employee':employee,'attendance_date':att_date,'docstatus':0})
				print(attn)
				status = ""
				if in_time and out_time:
					status = 'Absent'
				else:
					status = 'Absent'
				if not attn:
					att = frappe.new_doc('Attendance')
					att.employee = employee
					att.attendance_date = att_date
					att.status = status
					att.in_time = in_time
					att.out_time = out_time
					att.save(ignore_permissions=True)
					frappe.db.commit()
				else:
					if in_time:
						frappe.db.set_value('Attendance',attn,'in_time',in_time)
					if out_time:
						frappe.db.set_value('Attendance',attn,'out_time',out_time)

					frappe.db.set_value("Attendance",attn,'status',status)
				for c in checkins:
					print(c)
					frappe.db.set_value("Employee Checkin",c.name,"skip_auto_attendance",'1')
					frappe.db.set_value("Employee Checkin",c.name,"attendance",attn)
				
			
		if device in ['Mumbai']:
			if datetime.strptime('05:30:00','%H:%M:%S').time() < att_time < datetime.strptime('09:15:00','%H:%M:%S').time():
				if len(checkins) >= 2:
					in_time = checkins[0].time
					out_time = checkins[-1].time
				elif len(checkins) == 1:
					in_time = checkins[0].time
					out_time = checkins[-1].time
				attn = frappe.db.exists('Attendance',{'employee':employee,'attendance_date':att_date,'docstatus':0})
				print(attn)
				status = ""
				if in_time and out_time:
					if in_time == out_time:
						status = 'Absent'
					elif in_time != out_time:	
						status = 'Present'
				else:
					status = 'Absent'
				if not attn:
					att = frappe.new_doc('Attendance')
					att.employee = employee
					att.attendance_date = att_date
					att.status = status
					att.in_time = in_time
					att.out_time = out_time
					att.save(ignore_permissions=True)
					frappe.db.commit()
				else:
					if in_time:
						frappe.db.set_value('Attendance',attn,'in_time',in_time)
					if out_time:
						frappe.db.set_value('Attendance',attn,'out_time',out_time)

					frappe.db.set_value("Attendance",attn,'status',status)
				for c in checkins:
					print(c)
					frappe.db.set_value("Employee Checkin",c.name,"skip_auto_attendance",'1')
					frappe.db.set_value("Employee Checkin",c.name,"attendance",attn)
				
			elif datetime.strptime('09:15:00','%H:%M:%S').time() < att_time < datetime.strptime('12:15:00','%H:%M:%S').time():
				if len(checkins) >= 2:
					in_time = checkins[0].time
					out_time = checkins[-1].time
				elif len(checkins) == 1:
					in_time = checkins[0].time
					out_time = checkins[-1].time
				attn = frappe.db.exists('Attendance',{'employee':employee,'attendance_date':att_date,'docstatus':0})
				print(attn)
				status = ""
				if in_time and out_time:
					status = 'Absent'
				else:
					status = 'Absent'
				if not attn:
					att = frappe.new_doc('Attendance')
					att.employee = employee
					att.attendance_date = att_date
					att.status = status
					att.in_time = in_time
					att.out_time = out_time
					att.save(ignore_permissions=True)
					frappe.db.commit()
				else:
					if in_time:
						frappe.db.set_value('Attendance',attn,'in_time',in_time)
					if out_time:
						frappe.db.set_value('Attendance',attn,'out_time',out_time)
					frappe.db.set_value("Attendance",attn,'status',status)
				for c in checkins:
					print(c)
					frappe.db.set_value("Employee Checkin",c.name,"skip_auto_attendance",'1')
					frappe.db.set_value("Employee Checkin",c.name,"attendance",attn)
				

		elif device in ['CHENNAI']:
			if datetime.strptime('04:30:00','%H:%M:%S').time() < att_time < datetime.strptime('09:15:00','%H:%M:%S').time():
				if len(checkins) >= 2:
					in_time = checkins[0].time
					out_time = checkins[-1].time
				elif len(checkins) == 1:
					in_time = checkins[0].time
					out_time = checkins[-1].time
				attn = frappe.db.exists('Attendance',{'employee':employee,'attendance_date':att_date,'docstatus':0})
				print(attn)
				status = ""
				if in_time and out_time:
					if in_time == out_time:
						status = 'Absent'
					elif in_time != out_time:	
						status = 'Present'
				else:
					status = 'Absent'
				if not attn:
					att = frappe.new_doc('Attendance')
					att.employee = employee
					att.attendance_date = att_date
					att.status = status
					att.in_time = in_time
					att.out_time = out_time
					att.save(ignore_permissions=True)
					frappe.db.commit()
				else:
					if in_time:
						frappe.db.set_value('Attendance',attn,'in_time',in_time)
					if out_time:
						frappe.db.set_value('Attendance',attn,'out_time',out_time)

					frappe.db.set_value("Attendance",attn,'status',status)
				for c in checkins:
					print(c)
					frappe.db.set_value("Employee Checkin",c.name,"skip_auto_attendance",'1')
					frappe.db.set_value("Employee Checkin",c.name,"attendance",attn)
				
			elif datetime.strptime('09:15:00','%H:%M:%S').time() < att_time < datetime.strptime('12:15:00','%H:%M:%S').time():
				
				if len(checkins) >= 2:
					in_time = checkins[0].time
					out_time = checkins[-1].time
				elif len(checkins) == 1:
					in_time = checkins[0].time
					out_time = checkins[-1].time
				attn = frappe.db.exists('Attendance',{'employee':employee,'attendance_date':att_date,'docstatus':0})
				print(attn)
				status = ""
				if in_time and out_time:
					status = 'Absent'
				else:
					status = 'Absent'
				if not attn:
					att = frappe.new_doc('Attendance')
					att.employee = employee
					att.attendance_date = att_date
					att.status = status
					att.in_time = in_time
					att.out_time = out_time
					att.save(ignore_permissions=True)
					frappe.db.commit()
				else:
					if in_time:
						frappe.db.set_value('Attendance',attn,'in_time',in_time)
					if out_time:
						frappe.db.set_value('Attendance',attn,'out_time',out_time)

					frappe.db.set_value("Attendance",attn,'status',status)
				for c in checkins:
					print(c)
					frappe.db.set_value("Employee Checkin",c.name,"skip_auto_attendance",'1')
					frappe.db.set_value("Employee Checkin",c.name,"attendance",attn)
				
		elif device in ['SRICITY']:
			if datetime.strptime('05:30:00','%H:%M:%S').time() < att_time < datetime.strptime('11:15:00','%H:%M:%S').time():
				if len(checkins) >= 2:
					in_time = checkins[0].time
					out_time = checkins[-1].time
				elif len(checkins) == 1:
					in_time = checkins[0].time
					out_time = checkins[-1].time
				attn = frappe.db.exists('Attendance',{'employee':employee,'attendance_date':att_date})
				print(attn)
				status = ""
				if in_time and out_time:
					if in_time == out_time:
						status = 'Absent'
					elif in_time != out_time:	
						status = 'Present'
				else:
					status = 'Absent'
				if not attn:
					att = frappe.new_doc('Attendance')
					att.employee = employee
					att.attendance_date = att_date
					att.status = status
					att.in_time = in_time
					att.out_time = out_time
					att.save(ignore_permissions=True)
					frappe.db.commit()
				else:
					if in_time:
						frappe.db.set_value('Attendance',attn,'in_time',in_time)
					if out_time:
						frappe.db.set_value('Attendance',attn,'out_time',out_time)

					frappe.db.set_value("Attendance",attn,'status',status)
				for c in checkins:
					print(c)
					frappe.db.set_value("Employee Checkin",c.name,"skip_auto_attendance",'1')
					frappe.db.set_value("Employee Checkin",c.name,"attendance",attn)

			elif datetime.strptime('14:30:00','%H:%M:%S').time() < att_time < datetime.strptime('15:30:00','%H:%M:%S').time():
				if len(checkins) >= 2:
					in_time = checkins[0].time
					out_time = checkins[-1].time
				elif len(checkins) == 1:
					in_time = checkins[0].time
					out_time = checkins[-1].time
				attn = frappe.db.exists('Attendance',{'employee':employee,'attendance_date':att_date,'docstatus':0})
				print(attn)
				status = ""
				if in_time and out_time:
					if in_time == out_time:
						status = 'Absent'
					elif in_time != out_time:	
						status = 'Present'
				else:
					status = 'Absent'
				if not attn:
					att = frappe.new_doc('Attendance')
					att.employee = employee
					att.attendance_date = att_date
					att.status = status
					att.in_time = in_time
					att.out_time = out_time
					att.save(ignore_permissions=True)
					frappe.db.commit()
				else:
					if in_time:
						frappe.db.set_value('Attendance',attn,'in_time',in_time)
					if out_time:
						frappe.db.set_value('Attendance',attn,'out_time',out_time)
					frappe.db.set_value("Attendance",attn,'status',status)
				for c in checkins:
					print(c)
					frappe.db.set_value("Employee Checkin",c.name,"skip_auto_attendance",'1')
					frappe.db.set_value("Employee Checkin",c.name,"attendance",attn)
				
def get_total_working_hours():
	to_date = today()
	from_date= get_first_day(today())
	attendance = frappe.db.sql("""select name,employee,status,shift,in_time,out_time,attendance_date from `tabAttendance` where attendance_date between '%s' and '%s' """%(from_date,to_date),as_dict=True)	
	for att in attendance:
		if att.in_time and att.out_time:
			out_time = datetime.strptime(att.out_time, '%Y-%m-%d %H:%M:%S')
			str_time_out = out_time.strftime('%H:%M')
			in_time = datetime.strptime(att.in_time, '%Y-%m-%d %H:%M:%S')
			str_time_out = out_time.strftime('%H:%M')
			str_working_hours = out_time - in_time
			time_d_float = str_working_hours.total_seconds()
			whrs = time_d_float/3600
			total_working_hours = "{:.2f}".format(whrs)
			print(total_working_hours)			
			frappe.db.set_value('Attendance',att.name,'working_hours',total_working_hours)
				
			if float(total_working_hours) > 8:
				over_time_hours = float(total_working_hours) - 8
				frappe.db.set_value('Attendance',att.name,'ot',over_time_hours)
			if float(total_working_hours) < 4:
				
				frappe.set_value('Attendance',att.name,'status','Absent')
			elif float (total_working_hours) >=4 and float(total_working_hours) < 7.5:
				frappe.set_value('Attendance',att.name,'status','Half Day')
				frappe.set_value('Attendance',att.name,'leave_type','Leave Without Pay')	
			
def mark_absent_employee():

	from_date= get_first_day(today())
	to_date = today()

	att_date = today()
	yesterday = add_days(att_date,-1)
	employee = frappe.db.sql("""select * from `tabEmployee` where status = 'Active'""",as_dict =1)
	for emp in employee:
		dates = get_dates(from_date,to_date)
		
		for date in dates:
			day = date

			emp_doj = frappe.get_value('Employee',emp.name,'date_of_joining')
			if day >= emp_doj:
				emp_holiday_list = frappe.get_value('Employee',emp.name,'holiday_list')
				holiday = frappe.db.sql("""select `tabHoliday`.holiday_date,`tabHoliday`.weekly_off from `tabHoliday List` 
				left join `tabHoliday` on `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = '%s' and holiday_date = '%s' """%(emp_holiday_list,day),as_dict=True)
				if not holiday:
					att = frappe.db.exists("Attendance",{'employee':emp.name,'attendance_date':day})
					if not att:
						att_doc = frappe.new_doc('Attendance')
						att_doc.employee = emp.name
						att_doc.attendance_date = day
						att_doc.status = 'Absent'
						att_doc.save(ignore_permissions=True)

def create_hooks_mark_ot():
	job = frappe.db.exists('Scheduled Job Type', 'get_total_working_hours')
	if not job:
		sjt = frappe.new_doc("Scheduled Job Type")
		sjt.update({
			"method": 'hunter_douglas.mark_attendance.get_total_working_hours',
			"frequency": 'Cron',
			"cron_format": '10 11 * * *'
		})
		sjt.save(ignore_permissions=True)

def get_dates(from_date,to_date):
	no_of_days = date_diff(add_days(to_date, 1), from_date)
	dates = [add_days(from_date, i) for i in range(0, no_of_days)]
	return dates


@frappe.whitelist()
def del_att():
	att = frappe.db.sql(""" delete from `tabAttendance` where status != 'On Leave' and attendance_date between  '2022-12-25' and '2023-01-25'  """)