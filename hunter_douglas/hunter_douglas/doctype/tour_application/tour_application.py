# -*- coding: utf-8 -*-
# Copyright (c) 2018, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from datetime import datetime,timedelta
from frappe import _
from frappe.utils import today,flt,add_days,date_diff,getdate,cint,formatdate, getdate, get_link_to_form, \
    comma_or, get_fullname
from hunter_douglas.custom import update_attendance_by_app


class LeaveApproverIdentityError(frappe.ValidationError): pass
class OverlapError(frappe.ValidationError): pass
class InvalidLeaveApproverError(frappe.ValidationError): pass
class AttendanceAlreadyMarkedError(frappe.ValidationError): pass 

class TourApplication(Document):
    def on_submit(self):
        if self.status == "Applied":
            frappe.throw(_("Only Applications with status 'Approved' and 'Rejected' can be submitted"))
        # if self.status == "Approved":
        #     update_attendance_by_app(self.employee,self.from_date,self.to_date,self.from_date_session,self.to_date_session,"TR")


    def validate(self):
        self.validate_approver()
        self.validate_tour_overlap()	

    def validate_approver(self):
        if not frappe.session.user == 'hr.hdi@hunterdouglas.asia':
            employee = frappe.get_doc("Employee", self.employee)
            approvers = [l.leave_approver for l in employee.get("leave_approvers")]

            if len(approvers) and self.approver not in approvers:
                frappe.throw(_("Approver must be one of {0}")
                    .format(comma_or(approvers)), InvalidApproverError)

            elif self.approver and not frappe.db.sql("""select name from `tabHas Role`
                where parent=%s and role='Leave Approver'""", self.approver):
                frappe.throw(_("{0} ({1}) must have role 'Approver'")\
                    .format(get_fullname(self.approver), self.approver), InvalidApproverError)

            elif self.docstatus==0 and len(approvers) and self.approver != frappe.session.user:
                self.status = 'Applied'
                
            elif self.docstatus==1 and len(approvers) and self.approver != frappe.session.user:
                frappe.throw(_("Only the selected Approver can submit this Application"),
                    LeaveApproverIdentityError)
    
    def validate_tour_overlap(self):
        if not self.name:
            # hack! if name is null, it could cause problems with !=
            self.name = "New Tour Application"

        for d in frappe.db.sql("""
            select
                name, posting_date, from_date, to_date, total_number_of_days, half_day_date
            from `tabTour Application`
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
        msg = _("Employee {0} has already applied for Tour between {1} and {2}").format(self.employee,formatdate(d['from_date']), formatdate(d['to_date'])) \
            + """ <br><b><a href="#Form/Tour Application/{0}">{0}</a></b>""".format(d["name"])
        frappe.throw(msg, OverlapError)

    # def on_cancel(self):
    #     attendance_list = frappe.get_list("Attendance", {'employee': self.employee, 'on_duty_application': self.name})
    #     if attendance_list:
    #         for attendance in attendance_list:
    #             attendance_obj = frappe.get_doc("Attendance", attendance['name'])
    #             attendance_obj.cancel()
