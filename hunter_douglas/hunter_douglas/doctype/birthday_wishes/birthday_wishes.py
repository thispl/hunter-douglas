# -*- coding: utf-8 -*-
# Copyright (c) 2020, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import today
from datetime import date
import random
from frappe.model.document import Document

class BirthdayWishes(Document):
    pass

@frappe.whitelist()	
def send_birthday_wish():
    birthdays =frappe.db.sql("""select name,date_of_birth,company_email, employee_name
        from tabEmployee where day(date_of_birth) = day(%(date)s)
        and month(date_of_birth) = month(%(date)s)
        and status = 'Active'""",{"date": today()}, as_dict=True)
    for r in birthdays:
        print(r)
        wish = frappe.get_doc("Birthday Wishes")
        result=[]
        for w in wish.wishes:
            res=w.wishes
            result.append(res)
        s=random.sample(result,1)
        print(s)
        if birthdays:
            frappe.sendmail(recipients=['r.company_email'],
            subject="Birthday Wishes for {0}"),
            message="""<p> Dear {1} <br> {2} ,</p>""" .format(r.employee_name,r.employee_name,s)       