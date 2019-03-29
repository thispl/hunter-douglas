# -*- coding: utf-8 -*-
# Copyright (c) 2019, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from datetime import datetime,timedelta
import time
from frappe import _
from frappe.utils import today,flt,add_days,date_diff,getdate,cint,formatdate, getdate, get_link_to_form, \
    comma_or, get_fullname,cint
from hunter_douglas.hunter_douglas.doctype.on_duty_application.on_duty_application import validate_if_attendance_not_applicable

class LeaveApproverIdentityError(frappe.ValidationError): pass
class OverlapError(frappe.ValidationError): pass
class InvalidApproverError(frappe.ValidationError): pass
class AttendanceAlreadyMarkedError(frappe.ValidationError): pass

class CompensatoryOffApplication(Document):
    def on_submit(self):
        if self.status == "Applied":
            frappe.throw(_("Only Applications with status 'Approved' and 'Rejected' can be submitted"))

    def validate(self):
        self.validate_approver()
        self.validate_coff_overlap()	

    def validate_approver(self):
        if not frappe.session.user == 'hr.hdi@hunterdouglas.asia':
            employee = frappe.get_doc("Employee", self.employee)
            approvers = [l.leave_approver for l in employee.get("leave_approvers")]

            if len(approvers) and self.approver not in approvers:
                frappe.throw(_("Approver must be one of {0}").format(comma_or(approvers)), InvalidApproverError)

            elif self.approver and not frappe.db.sql("""select name from `tabHas Role`
                where parent=%s and role='Leave Approver'""", self.approver):
                frappe.throw(_("{0} ({1}) must have role 'Approver'").format(get_fullname(self.approver), self.approver), InvalidApproverError)

            elif self.docstatus==0 and len(approvers) and self.approver != frappe.session.user:
                self.status = 'Applied'
                
            elif self.docstatus==1 and len(approvers) and self.approver != frappe.session.user:
                frappe.throw(_("Only the selected Approver can submit this Application"),LeaveApproverIdentityError)
    
    def validate_coff_overlap(self):
        if not self.name:
            # hack! if name is null, it could cause problems with !=
            self.name = "New Compensatory Off Application"

        for d in frappe.db.sql("""
            select
                name, posting_date, from_date, to_date, total_number_of_days, half_day_date
            from `tabCompensatory Off Application`
            where employee = %(employee)s and docstatus < 2 and status in ("Open","Applied", "Approved")
            and to_date >= %(from_date)s and from_date <= %(to_date)s
            and name != %(name)s""", {
                "employee": self.employee,
                "from_date": self.from_date,
                "to_date": self.to_date,
                "name": self.name
            }, as_dict = 1):

            if cint(self.half_day)==1 and getdate(self.half_day_date) == getdate(d.half_day_date) and (
                flt(self.total_leave_days)==0.5
                or getdate(self.from_date) == getdate(d.to_date)
                or getdate(self.to_date) == getdate(d.from_date)):

                total_leaves_on_half_day = self.get_total_leaves_on_half_day()
                if total_leaves_on_half_day >= 1:
                    self.throw_overlap_error(d)
            else:
                self.throw_overlap_error(d)

    def throw_overlap_error(self, d):
        msg = _("Employee {0} has already applied for C-OFF between {1} and {2}").format(self.employee,formatdate(d['from_date']), formatdate(d['to_date'])) \
            + """ <br><b><a href="#Form/Compensatory Off Application/{0}">{0}</a></b>""".format(d["name"])
        frappe.throw(msg, OverlapError)

@frappe.whitelist()
def get_number_of_leave_days(employee, from_date, to_date,from_date_session=None,  to_date_session=None, date_dif=None):
    number_of_days = 0
    if from_date == to_date:
        if from_date_session != 'Full Day':
            number_of_days = 0.5
        else:
            number_of_days = 1
    else:
        if from_date_session == "Full Day" and to_date_session == "Full Day":
            number_of_days = flt(date_dif)
        if from_date_session == "Full Day" and to_date_session == "First Half":
            number_of_days = flt(date_dif) - 0.5
        if from_date_session == "Second Half" and to_date_session == "Full Day":
            number_of_days = flt(date_dif) - 0.5
        if from_date_session == "Second Half" and to_date_session == "First Half":
            number_of_days = flt(date_dif) - 1
    return number_of_days

@frappe.whitelist()
def get_number_of_required_hours(employee, from_date, to_date,from_date_session=None,  to_date_session=None, date_dif=None,current_balance=None):
    number_of_days = 0
    if from_date == to_date:
        if from_date_session != 'Full Day':
            number_of_days = 0.5
        else:
            number_of_days = 1
    else:
        if from_date_session == "Full Day" and to_date_session == "Full Day":
            number_of_days = flt(date_dif)
        if from_date_session == "Full Day" and to_date_session == "First Half":
            number_of_days = flt(date_dif) - 0.5
        if from_date_session == "Second Half" and to_date_session == "Full Day":
            number_of_days = flt(date_dif) - 0.5
        if from_date_session == "Second Half" and to_date_session == "First Half":
            number_of_days = flt(date_dif) - 1
    cur_hour = current_balance.split(":")
    cur_balance = timedelta(hours =cint(cur_hour[0]),minutes=cint(cur_hour[1]))
    required_balance = timedelta(hours =(number_of_days * 8))
    reqd_balance =  "%02d:00:00" % (number_of_days * 8)
    if cur_balance < required_balance:
        return "less"
        # frappe.throw("Balance is Less for the Applied Days") 
    else:    
        return reqd_balance



@frappe.whitelist()
def reduce_comp_off_balance(employee,total_number_of_days):
    coff_id = frappe.db.exists("Comp Off Details",{"employee":employee})
    if coff_id:
        coff = frappe.get_doc("Comp Off Details",coff_id)
        # child = coff.comp_off_calculation_details
        # frappe.errprint(coff.total_hours)
        # h = t
        # frappe.errprint(h)
        # t1 = total_number_of_days.total_seconds()  
        # minutes = t1 // 60
        # hours = minutes // 60
        # t3 =  "%02d:%02d:%02d" % (hours, minutes % 60, t1 % 60)
        # frappe.errprint(t3)



@frappe.whitelist()
def remove_child(req_bal,employee):
    coff_details = frappe.get_doc("Comp Off Details",employee)
    child = coff_details.comp_off_calculation_details
    for c in child:
        FMT = '%H:%M:%S'
        hour_bal = str(c.hours)
        diff = datetime.strptime(hour_bal, FMT) - datetime.strptime(req_bal, FMT)
        # modified_req_bal = req_bal.split(":")
        # hours =cint(modified_req_bal[0])
        # minutes=cint(modified_req_bal[1])
        # modified_hour_bal = hour_bal.split(":")
        # hours1 =cint(modified_hour_bal[0])
        # minutes1=cint(modified_hour_bal[1])
        # hour_diff = hours - hours1
        # minutes_diff = minutes - minutes1
        frappe.errprint(diff)
        # frappe.errprint(minutes_diff)