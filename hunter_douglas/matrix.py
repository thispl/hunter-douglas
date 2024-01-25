
from __future__ import unicode_literals
import json
import frappe

@frappe.whitelist(allow_guest=True)
def attendance(**args):
    args = frappe._dict(args)
    frappe.log_error(args, "from_matrix") 