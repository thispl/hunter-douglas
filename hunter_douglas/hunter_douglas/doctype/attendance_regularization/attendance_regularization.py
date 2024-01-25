# Copyright (c) 2022, teampro and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from email import message
import re
from frappe import _
import frappe
from frappe.model.document import Document
from datetime import date, timedelta, datetime,time
from frappe.utils import (getdate, cint, add_months, date_diff, add_days,
	nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime,today, format_date)
import pandas as pd
import math
from frappe.utils import add_months, cint, flt, getdate, time_diff_in_hours




class AttendanceRegularization(Document):

	def on_submit(self):
		status = self.validate_total_wh()
		att_status = status[0]['status']
		att_working_hours = self.validate_total_wh()
		working_hours = att_working_hours[0]['att_wh']
		
		hh = self.validate_check_holiday()
		if not hh:
			att = frappe.db.exists('Attendance',{'employee':self.employee,'attendance_date':self.attendance_date,'docstatus':('!=','2')})
			if att:
				attendance = frappe.get_doc('Attendance',{'name':att})
				attendance.status = att_status
				attendance.in_time = self.corrected_in_time
				attendance.out_time = self.corrected_out_time
				attendance.status = self.corrected_status
				attendance.working_hours = self.corrected_total_working_hours
				attendance.ot = self.corrected_overtime_hours
				attendance.save(ignore_permissions=True)
				frappe.db.commit()
				
				frappe.db.set_value('Attendance',att,'matched_status','Matched')
				frappe.db.set_value('Attendance',att,'attendance_regularize',self.name)
				frappe.db.sql(""" update `tabAttendance` set docstatus = 1 where name = '%s' """%(att))

		else:
			att = frappe.db.exists('Attendance',{'name':self.attendance_marked})
			if att:
				total_working_hour = self.validate_total_wh()
				total_wh = total_working_hour[0]['total_wh']
				ftr = [3600,60,1]
				hr = sum([a*b for a,b in zip(ftr, map(int,str(total_wh).split(':')))])
				wh = round(hr/3600,1)
				if wh > 0:
					none_time =pd.to_datetime('00:00:00').time()
					holiday_ot_hr = (math.floor(wh * 2) / 2) - 0.5
					attendance = frappe.get_doc('Attendance',{'name':self.attendance_marked})
					attendance.status = 'Present'
					attendance.in_time = self.corrected_in_time
					attendance.out_time = self.corrected_out_time
					attendance.working_hours = self.corrected_total_working_hours
					attendance.ot = self.corrected_overtime_hours
					attendance.status = self.corrected_status
					attendance.save(ignore_permissions=True)
					frappe.db.commit()
					frappe.db.set_value('Attendance',self.attendance_marked,'status','Present')
					frappe.db.set_value('Attendance',self.attendance_marked,' ','Matched')
					frappe.db.set_value('Attendance',self.attendance_marked,'attendance_regularize',self.name)
					frappe.db.sql(""" update `tabAttendance` set docstatus = 1 where name = '%s' """%(att))

				   
	def on_cancel(self):
		att = frappe.db.exists('Attendance',{'employee':self.employee,'attendance_date':self.attendance_date})
		if att:
			att_reg = frappe.db.get_value('Attendance',{'name':att},['attendance_regularize'])
			if att_reg == self.name:
				frappe.db.sql(""" update `tabAttendance` set attendance_regularize = '' where name = '%s' and docstatus != 2 """%(att))
				frappe.db.sql(""" update `tabAttendance` set matched_status = 'Unmatched' where name = '%s' and docstatus != 2 """%(att))
				frappe.db.sql(""" update `tabAttendance` set docstatus = 0 where name = '%s' """%(att))

	def validate_total_wh(self):
		datalist = []
		data = {}
		work_hour = time_diff_in_hours(self.corrected_out_time,self.corrected_in_time)
		str_in_time = datetime.strptime(str(self.corrected_in_time),'%Y-%m-%d %H:%M:%S')
		str_out_time = datetime.strptime(str(self.corrected_out_time),'%Y-%m-%d %H:%M:%S')
		total_wh = str_out_time - str_in_time
		if work_hour < 4.0:
			status = 'Absent'
		elif work_hour >= 4.0 and work_hour < 8.0:
			status = 'Half Day'
		elif work_hour >= 8.0:
			status = 'Present'	
		total_wh_att = datetime.strptime(str(total_wh),'%H:%M:%S').strftime('%H:%M')
		ftr = [3600,60,1]
		hr = sum([a*b for a,b in zip(ftr, map(int,str(total_wh).split(':')))])
		att_wh = round(hr/3600,1)
		data.update({
			'status':status,
			'total_wh':total_wh,
			'att_wh':att_wh,
			'total_wh_att':total_wh_att,
		})
		datalist.append(data.copy())
		return datalist  


	def validate_check_holiday(self):
		holiday_list = frappe.db.get_value('Employee',self.employee,'holiday_list')
		holiday = frappe.db.sql("""select `tabHoliday`.holiday_date,`tabHoliday`.weekly_off from `tabHoliday List` 
		left join `tabHoliday` on `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = '%s' and holiday_date = '%s' """%(holiday_list,self.attendance_date),as_dict=True)
		if holiday:
			if holiday[0].weekly_off == 1:
				return "WW"
			else:
				return "HH"

@frappe.whitelist()
def get_attendance(emp,att_date):
	datalist = []
	data = {}
	if frappe.db.exists('Attendance',{'employee':emp,'attendance_date':att_date}):
		if frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':att_date},['in_time']):
			in_time = frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':att_date},['in_time']) 
		else:
			in_time = '-'    
		if frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':att_date},['out_time']):
			out_time = frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':att_date},['out_time'])   
		else:
			out_time = '-'
		data.update({
			'in_time':in_time,
			'out_time':out_time,
		})
		datalist.append(data.copy())

	else:
		frappe.throw(_("Employee has No Checkins for the day"))
		data.update({
			'in_time':'No In Time',
			'out_time':'',
		})
		datalist.append(data.copy())
	return datalist    

@frappe.whitelist()
def attendance_marked(emp,att_date):
	datalist = []
	data = {}
	actual_shift = ''
	total_working_hours = ''
	overtime_hours = ''
	att_id = ''
	status_ =''
	if frappe.db.exists('Attendance',{'employee':emp,'attendance_date':att_date}):
		if frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':att_date},['in_time']):
			in_time = frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':att_date},['in_time'])
			# actual_shift = frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':att_date},['actual_shift'])
			total_working_hours = frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':att_date},['working_hours'])
			overtime_hours = frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':att_date},['ot'])
			status_ = frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':att_date},['status'])
			
			att_id = frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':att_date},['name'])
		else:
			in_time = ''   
		if frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':att_date},['out_time']):
			out_time = frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':att_date},['out_time'])
			total_working_hours = frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':att_date},['working_hours'])
			overtime_hours = frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':att_date},['ot'])
			status_ = frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':att_date},['status'])
			att_id = frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':att_date},['name'])
		else:
			out_time = ''
		data.update({
			'in_time':in_time,
			'out_time':out_time,
			'total_working_hours':total_working_hours,
			'att_id':att_id,
			'overtime_hours':overtime_hours,
			'status_':status_
		})
		datalist.append(data.copy())
	   
	else:
		frappe.throw(_("Employee has No Checkins for the day"))
		data.update({
			'in_time':'-',
			'out_time':'-',
			'total_working_hours':'-',
			'overtime_hours':'-',
			'status_':'-'
		})
		datalist.append(data.copy())
	return datalist 