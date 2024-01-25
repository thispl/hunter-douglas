# -*- coding: utf-8 -*-
# Copyright (c) 2021, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class OTApproval(Document):
	def update_attendance(self,row):
		ts =frappe.new_doc("Timesheet")
		ts.employee =row['employee']
		ts.append("time_logs",{
			"hours":row['overtime'],
			"from_time":row["from_time"],
			"to_time":row["to_time"]
		})
		ts.save(ignore_permissions =True)
		frappe.db.commit()
