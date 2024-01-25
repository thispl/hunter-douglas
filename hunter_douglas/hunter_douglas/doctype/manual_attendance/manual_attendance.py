# -*- coding: utf-8 -*-
# Copyright (c) 2021, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class ManualAttendance(Document):
	def validate(self):
		if (self.attendance_status == "Approved"):
			at =frappe.new_doc("Attendance")
			at.employee = self.employee
			at.status = "Present"
			at.in_time = self.in_time
			at.attendance_date =self.attendance_date
			at.company = "Hunter Douglas India Pvt. Ltd."
			at.out_time =self.out_time
			at.save(ignore_permissions =True)
			frappe.db.commit()
