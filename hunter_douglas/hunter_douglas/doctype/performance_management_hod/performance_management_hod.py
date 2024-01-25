# -*- coding: utf-8 -*-
# Copyright (c) 2019, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import frappe,json
from frappe.model.document import Document
from datetime import datetime
from frappe.utils import (getdate, cint, add_months, date_diff, add_days,
	nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime)
from dateutil import relativedelta


class PerformanceManagementHOD(Document):
	pass
	# def validate(self): 
	# 	date_of_joining = self.date_of_joining
	# 	date_object = datetime.strptime(date_of_joining, '%Y-%m-%d')
	# 	current_date = getdate(datetime.now())
	# 	hd_experience = current_date.year - date_object.year
	# 	self.hdi_experience = hd_experience
	# 	in_exp = int(self.out_experience or 0) 
	# 	self.total_experience = int(self.hdi_experience or 0) + in_exp
