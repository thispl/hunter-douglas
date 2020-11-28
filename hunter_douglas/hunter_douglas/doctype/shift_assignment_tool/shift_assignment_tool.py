# -*- coding: utf-8 -*-
# Copyright (c) 2019, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe,json
from frappe.model.document import Document

class ShiftAssignmentTool(Document):
    pass



@frappe.whitelist()
def update_shift(shift_assignment_tool_kit):
    sat = {}
    sat = json.loads(shift_assignment_tool_kit)
    for sa in sat:
        employee = sa.get("employee")
        from_date = sa.get("from_date")
        to_date = sa.get("to_date")
        shift = sa.get("shift")
        shift = shift.split("(")
        shift = shift[0]
        if shift:
            nsa = frappe.new_doc("Shift Assignment")
            nsa.update({
                "employee": employee,
                "from_date": from_date,
                "to_date": to_date,
                "shift": shift
            })
            nsa.save(ignore_permissions=True)
    return "Ok"