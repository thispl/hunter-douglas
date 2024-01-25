# -*- coding: utf-8 -*-
# Copyright (c) 2019, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe,json
from frappe.model.document import Document
from datetime import datetime
from frappe.utils import (getdate, cint, add_months, date_diff, add_days,
	nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime)
from dateutil import relativedelta 

class PerformanceManagementSelf(Document):
	def validate(self): 
		date_of_joining = self.date_of_joining
		date_object = datetime.strptime(date_of_joining, '%Y-%m-%d')
		current_date = getdate(datetime.now())
		hd_experience = current_date.year - date_object.year
		self.hd_experience = hd_experience
		in_exp = int(self.in_experience or 0) 
		self.total_experience = int(self.hd_experience or 0) + in_exp


@frappe.whitelist()
def sort_r(table):
	in_time = {}
	in_time = json.loads(table)
	sort = sorted(in_time, key=lambda k: k['competency'],reverse=True)
	return sort




   