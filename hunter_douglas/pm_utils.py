# -*- coding: utf-8 -*-
# Copyright (c) 2017, VHRS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe,os,base64
import requests
import datetime
import json,calendar
from datetime import datetime,timedelta,date,time
import datetime as dt
from frappe.utils import cint,today,flt,date_diff,add_days,add_months,date_diff,getdate,formatdate,cint,cstr
from frappe.desk.notifications import delete_notification_count_for
from frappe import _

@frappe.whitelist()
def update_pm_manager(doc, method):
    if doc.manager:
        pmm = frappe.db.get_value("Performance Management Manager", {
                                      "employee_code": doc.employee_code,"appraisal_year":doc.appraisal_year})
        if pmm:
            epmm = frappe.get_doc("Performance Management Manager", pmm)
        else:
            epmm = frappe.new_doc("Performance Management Manager")
        epmm.update({
            "employee_code": doc.employee_code,
            "employee_code1": doc.employee_code,
            "cost_code": doc.cost_code,
            "department": doc.department,
            "year_of_last_promotion": doc.year_of_last_promotion,
            "business_unit": doc.business_unit,
            "grade": doc.grade,
            "employee_name": doc.employee_name,
            "manager": doc.manager,
            "hod": doc.hod,
            "reviewer": doc.reviewer,
            "designation": doc.designation,
            "date_of_joining": doc.date_of_joining,
            "appraisal_year": doc.appraisal_year,
            "location": doc.location,
            "out_experience":doc.in_experience,
            "hdi_experience":doc.hd_experience,
            "total_experience":doc.total_experience,
            "no_of_promotion": doc.no_of_promotion,
            "small_text_12": doc.small_text_12,
            "small_text_14": doc.small_text_14,
            "small_text_16": doc.small_text_16,
            "small_text_18": doc.small_text_18,
            "required__job_knowledge": doc.required__job_knowledge,
            "training_required_to_enhance_job_knowledge": doc.training_required_to_enhance_job_knowledge,
            "required_skills": doc.required_skills,
            "training_required__to_enhance_skills_competencies": doc.training_required__to_enhance_skills_competencies
        })
        epmm.set('sales_target', [])
        child = doc.sales_target
        for c in child:
            epmm.append("sales_target",{
                "year": c.year,
                "actual_targets": c.actual_targets,
                "attained_targets": c.attained_targets,
                "order_booked":c.order_booked
            })
        epmm.set('job_analysis', [])
        child1 = doc.job_analysis
        for c in child1:
            epmm.append("job_analysis",{
                "appraisee_remarks": c.appraisee_remarks
            })
        epmm.set('competency_assessment1', [])
        child2 = doc.competency_assessment1
        for c in child2:
            epmm.append("competency_assessment1",{
                "competency": c.competency,
                "weightage": c.weightage,
                "appraisee_weightage": c.appraisee_weightage,
                "manager": c.appraisee_weightage
            })
        epmm.set('key_result_area', [])
        child3 = doc.key_result_area
        for c in child3:
            if c.manager:
                epmm.append("key_result_area",{
                    "goal_setting_for_current_year": c.goal_setting_for_current_year,
                    "performance_measure": c.performance_measure,
                    "weightage_w_100": c.weightage_w_100,
                    "self_rating": c.self_rating,
                    "manager": c.manager,
                    "weightage": c.weightage,
                    "hod":c.hod,
                    "reviewer":c.reviewer
                })
            else:
                epmm.append("key_result_area",{
                    "goal_setting_for_current_year": c.goal_setting_for_current_year,
                    "performance_measure": c.performance_measure,
                    "weightage_w_100": c.weightage_w_100,
                    "self_rating": c.self_rating,
                    "manager": c.self_rating,
                    "weightage": c.weightage,
                })
        epmm.set('key_results_area', [])
        child4 = doc.key_results_area
        for c in child4:
            epmm.append("key_results_area",{
                "goal_setting_for_last_year": c.goal_setting_for_last_year,
                "performance_measure": c.performance_measure,
                "weightage_w_100": c.weightage_w_100,
                "self_rating": c.self_rating,
                "weightage": c.weightage,
            })
        epmm.save(ignore_permissions=True)
    else:
        pmm = frappe.db.get_value("Performance Management HOD", {
                                      "employee_code": doc.employee_code,"appraisal_year":doc.appraisal_year})
        if pmm:
            epmm = frappe.get_doc("Performance Management HOD", pmm)
        else:
            epmm = frappe.new_doc("Performance Management HOD")
        epmm.update({
            "employee_code": doc.employee_code,
            "employee_code1": doc.employee_code,
            "cost_code": doc.cost_code,
            "department": doc.department,
            "year_of_last_promotion": doc.year_of_last_promotion,
            "business_unit": doc.business_unit,
            "grade": doc.grade,
            "employee_name": doc.employee_name,
            "manager": doc.manager,
            "hod": doc.hod,
            "reviewer": doc.reviewer,
            "designation": doc.designation,
            "date_of_joining": doc.date_of_joining,
            "appraisal_year": doc.appraisal_year,
            "location": doc.location,
            "out_experience":doc.in_experience,
            "hdi_experience":doc.hd_experience,
            "total_experience":doc.total_experience,
            "no_of_promotion": doc.no_of_promotion,
            "small_text_12": doc.small_text_12,
            "small_text_14": doc.small_text_14,
            "small_text_16": doc.small_text_16,
            "small_text_18": doc.small_text_18,
            "potential": "-",
            "performance": "-",
            "promotion": "-",
            "any_other_observations": "-",
            "required__job_knowledge": doc.required__job_knowledge,
            "training_required_to_enhance_job_knowledge": doc.training_required_to_enhance_job_knowledge,
            "required_skills": doc.required_skills,
            "training_required__to_enhance_skills_competencies": doc.training_required__to_enhance_skills_competencies
        })
        epmm.set('sales_target', [])
        child = doc.sales_target
        for c in child:
            epmm.append("sales_target",{
                "year": c.year,
                "actual_targets": c.actual_targets,
                "attained_targets": c.attained_targets,
                "order_booked":c.order_booked

            })
        epmm.set('job_analysis', [])
        child1 = doc.job_analysis
        for c in child1:
            epmm.append("job_analysis",{
                "appraisee_remarks": c.appraisee_remarks,
                "appraiser_remarks": "-"
            })
        epmm.set('competency_assessment1', [])
        child2 = doc.competency_assessment1
        for c in child2:
            epmm.append("competency_assessment1",{
                "competency": c.competency,
                "weightage": c.weightage,
                "appraisee_weightage": c.appraisee_weightage,
                "manager": "-",
                "hod": c.appraisee_weightage
            })
        epmm.set('key_result_area', [])
        child3 = doc.key_result_area
        for c in child3:
            epmm.append("key_result_area",{
                "goal_setting_for_current_year": c.goal_setting_for_current_year,
                "performance_measure": c.performance_measure,
                "weightage_w_100": c.weightage_w_100,
                "self_rating": c.self_rating,
                "weightage": c.weightage,
                "manager": "-",
                "hod": c.self_rating
            })
        epmm.set('key_results_area', [])
        child4 = doc.key_results_area
        for c in child4:
            epmm.append("key_results_area",{
                "goal_setting_for_last_year": c.goal_setting_for_last_year,
                "performance_measure": c.performance_measure,
                "weightage_w_100": c.weightage_w_100,
                "weightage": c.weightage,
                "self_rating": c.self_rating
            })
        epmm.set('employee_feedback', [])
        # child5 = doc.employee_feedback
        for c in range(5):
            epmm.append("employee_feedback",{
                "appraisee_remarks": "-"
            })
        epmm.save(ignore_permissions=True)

@frappe.whitelist()
def update_pm_hod(doc, method):
    if doc.manager == frappe.session.user:
        pmm = frappe.db.get_value("Performance Management HOD", {
                                      "employee_code": doc.employee_code,"appraisal_year":doc.appraisal_year})
        if pmm:
            epmm = frappe.get_doc("Performance Management HOD", pmm)
        else:
            epmm = frappe.new_doc("Performance Management HOD")
        epmm.update({
            "employee_code": doc.employee_code,
            "employee_code1": doc.employee_code,
            "cost_code": doc.cost_code,
            "department": doc.department,
            "year_of_last_promotion": doc.year_of_last_promotion,
            "business_unit": doc.business_unit,
            "grade": doc.grade,
            "employee_name": doc.employee_name,
            "manager": doc.manager,
            "hod": doc.hod,
            "reviewer": doc.reviewer,
            "designation": doc.designation,
            "date_of_joining": doc.date_of_joining,
            "appraisal_year": doc.appraisal_year,
            "location": doc.location,
            "out_experience":doc.in_experience,
            "hdi_experience":doc.hd_experience,
            "total_experience":doc.total_experience,
            "no_of_promotion": doc.no_of_promotion,
            "small_text_12": doc.small_text_12,
            "small_text_14": doc.small_text_14,
            "small_text_16": doc.small_text_16,
            "small_text_18": doc.small_text_18,
            "potential": doc.potential,
            "performance": doc.performance,
            "promotion": doc.promotion,
            "any_other_observations": doc.any_other_observations,
            "potential_hod": doc.potential,
            "performance_hod": doc.performance,
            "promotion_hod": doc.promotion,
            "any_other_observations_hod": doc.any_other_observations,
            "required__job_knowledge": doc.required__job_knowledge,
            "training_required_to_enhance_job_knowledge": doc.training_required_to_enhance_job_knowledge,
            "required_skills": doc.required_skills,
            "training_required__to_enhance_skills_competencies": doc.training_required__to_enhance_skills_competencies
        })
        epmm.set('sales_target', [])
        child = doc.sales_target
        for c in child:
            epmm.append("sales_target",{
                "year": c.year,
                "actual_targets": c.actual_targets,
                "attained_targets": c.attained_targets,
                "order_booked":c.order_booked

            })
        epmm.set('job_analysis', [])
        child1 = doc.job_analysis
        for c in child1:
            epmm.append("job_analysis",{
                "appraisee_remarks": c.appraisee_remarks,
                "appraiser_remarks": c.appraiser_remarks
            })
        epmm.set('competency_assessment1', [])
        child2 = doc.competency_assessment1
        for c in child2:
            epmm.append("competency_assessment1",{
                "competency": c.competency,
                "weightage": c.weightage,
                "appraisee_weightage": c.appraisee_weightage,
                "manager": c.manager,
                "hod": c.manager
            })
        epmm.set('key_result_area', [])
        child3 = doc.key_result_area
        for c in child3:
            if c.hod:
                epmm.append("key_result_area",{
                    "goal_setting_for_current_year": c.goal_setting_for_current_year,
                    "performance_measure": c.performance_measure,
                    "weightage_w_100": c.weightage_w_100,
                    "self_rating": c.self_rating,
                    "weightage": c.weightage,
                    "manager": c.manager,
                    "hod": c.hod,
                    "reviewer":c.reviewer
                })
            else:
                epmm.append("key_result_area",{
                "goal_setting_for_current_year": c.goal_setting_for_current_year,
                "performance_measure": c.performance_measure,
                "weightage_w_100": c.weightage_w_100,
                "self_rating": c.self_rating,
                "weightage": c.weightage,
                "manager": c.manager,
                "hod": c.manager
            })
        epmm.set('key_results_area', [])
        child4 = doc.key_results_area
        for c in child4:
            epmm.append("key_results_area",{
                "goal_setting_for_last_year": c.goal_setting_for_last_year,
                "performance_measure": c.performance_measure,
                "weightage_w_100": c.weightage_w_100,
                "weightage": c.weightage,
                "self_rating": c.self_rating
            })
        epmm.set('employee_feedback', [])
        child5 = doc.employee_feedback
        for c in child5:
            epmm.append("employee_feedback",{
                "appraisee_remarks": c.appraisee_remarks
            })
        epmm.save(ignore_permissions=True)
    
@frappe.whitelist()
def update_pm_reviewer(doc, method):
    if doc.hod:
        pmm = frappe.db.get_value("Performance Management Reviewer", {
                                        "employee_code": doc.employee_code,"appraisal_year":doc.appraisal_year})
        if pmm:
            epmm = frappe.get_doc("Performance Management Reviewer", pmm)
        else:
            epmm = frappe.new_doc("Performance Management Reviewer")
        epmm.update({
            "employee_code": doc.employee_code,
            "employee_code1": doc.employee_code,
            "cost_code": doc.cost_code,
            "department": doc.department,
            "year_of_last_promotion": doc.year_of_last_promotion,
            "business_unit": doc.business_unit,
            "grade": doc.grade,
            "employee_name": doc.employee_name,
            "manager": doc.manager,
            "hod": doc.hod,
            "reviewer": doc.reviewer,
            "designation": doc.designation,
            "date_of_joining": doc.date_of_joining,
            "appraisal_year": doc.appraisal_year,
            "location": doc.location,
            "out_experience":doc.out_experience,
            "hdi_experience":doc.hdi_experience,
            "total_experience":doc.total_experience,
            "no_of_promotion": doc.no_of_promotion,
            "small_text_12": doc.small_text_12,
            "small_text_14": doc.small_text_14,
            "small_text_16": doc.small_text_16,
            "small_text_18": doc.small_text_18,
            "potential": doc.potential,
            "performance": doc.performance,
            "promotion": doc.promotion,
            "any_other_observations": doc.any_other_observations,
            "potential_hod": doc.potential_hod,
            "performance_hod": doc.performance_hod,
            "promotion_hod": doc.promotion_hod,
            "any_other_observations_hod": doc.any_other_observations_hod,
            "required__job_knowledge": doc.required__job_knowledge,
            "training_required_to_enhance_job_knowledge": doc.training_required_to_enhance_job_knowledge,
            "required_skills": doc.required_skills,
            "training_required__to_enhance_skills_competencies": doc.training_required__to_enhance_skills_competencies
        })
        epmm.set('sales_target', [])
        child = doc.sales_target
        for c in child:
            epmm.append("sales_target",{
                "year": c.year,
                "actual_targets": c.actual_targets,
                "attained_targets": c.attained_targets,
                "order_booked":c.order_booked

            })
        epmm.set('job_analysis', [])
        child1 = doc.job_analysis
        for c in child1:
            epmm.append("job_analysis",{
                "appraisee_remarks": c.appraisee_remarks,
                "appraiser_remarks": c.appraiser_remarks
            })
        epmm.set('competency_assessment1', [])
        child2 = doc.competency_assessment1
        for c in child2:
            epmm.append("competency_assessment1",{
                "competency": c.competency,
                "weightage": c.weightage,
                "appraisee_weightage": c.appraisee_weightage,
                "appraiser_rating": c.manager,
                "hod": c.hod,
                "reviewer": c.hod
            })
        epmm.set('key_result_area', [])
        child3 = doc.key_result_area
        for c in child3:
            if c.reviewer:
                epmm.append("key_result_area",{
                    "goal_setting_for_current_year": c.goal_setting_for_current_year,
                    "performance_measure": c.performance_measure,
                    "weightage_w_100": c.weightage_w_100,
                    "weightage": c.weightage,
                    "self_rating": c.self_rating,
                    "appraiser_rating_r": c.manager,
                    "hod": c.hod,
                    "reviewer": c.reviewer
                })
            else:
                epmm.append("key_result_area",{
                    "goal_setting_for_current_year": c.goal_setting_for_current_year,
                    "performance_measure": c.performance_measure,
                    "weightage_w_100": c.weightage_w_100,
                    "weightage": c.weightage,
                    "self_rating": c.self_rating,
                    "appraiser_rating_r": c.manager,
                    "hod": c.hod,
                    "reviewer": c.hod
                })
        epmm.set('key_results_area', [])
        child4 = doc.key_results_area
        for c in child4:
            epmm.append("key_results_area",{
                "goal_setting_for_last_year": c.goal_setting_for_last_year,
                "performance_measure": c.performance_measure,
                "weightage_w_100": c.weightage_w_100,
                "weighted_score": c.weightage,
            })
        epmm.set('employee_feedback', [])
        child5 = doc.employee_feedback
        for c in child5:
            epmm.append("employee_feedback",{
                "appraisee_remarks": c.appraisee_remarks,
                "hod": c.hod
            })
        pm = frappe.db.exists("Performance Management Reviewer",{"employee_code": doc.employee_code,"appraisal_year":(cint(doc.appraisal_year) - 1)})
        if pm:
            employeedoc = frappe.get_doc("Performance Management Reviewer",pm)
            if employeedoc:
                epmm.set('management_pm_details', [])
                child6 = employeedoc.management_pm_details
                for c in child6:
                    epmm.append("management_pm_details",{
                        "year": c.year,
                        "hike": c.hike
                    })
        else:
            employee_appraisal_info = frappe.db.exists("Employee",{"name": doc.employee_code})
            if employee_appraisal_info:
                employeedoc = frappe.get_doc("Employee",employee_appraisal_info)
                if employeedoc:
                    epmm.set('management_pm_details', [])
                    child6 = employeedoc.pm_appraisal_info
                    for c in child6:
                        epmm.append("management_pm_details",{
                            "year": c.year,
                            "hike": c.hike
                        })
        epmm.save(ignore_permissions=True)

    
@frappe.whitelist()
def update_pm_reviewers():
    self_list = ["PMH0414"]
    for s in self_list:
        doc = frappe.get_doc("Performance Management HOD", s)
        pmm = frappe.db.get_value("Performance Management Reviewer", {
                                        "employee_code": doc.employee_code,"appraisal_year":doc.appraisal_year})
        if pmm:
            epmm = frappe.get_doc("Performance Management Reviewer", pmm)
        else:
            epmm = frappe.new_doc("Performance Management Reviewer")
        epmm.update({
            "employee_code": doc.employee_code,
            "employee_code1": doc.employee_code,
            "cost_code": doc.cost_code,
            "department": doc.department,
            "year_of_last_promotion": doc.year_of_last_promotion,
            "business_unit": doc.business_unit,
            "grade": doc.grade,
            "employee_name": doc.employee_name,
            "manager": doc.manager,
            "hod": doc.hod,
            "reviewer": doc.reviewer,
            "designation": doc.designation,
            "date_of_joining": doc.date_of_joining,
            "appraisal_year": doc.appraisal_year,
            "location": doc.location,
            "out_experience":doc.out_experience,
            "hdi_experience":doc.hdi_experience,
            "total_experience":doc.total_experience,
            "no_of_promotion": doc.no_of_promotion,
            "small_text_12": doc.small_text_12,
            "small_text_14": doc.small_text_14,
            "small_text_16": doc.small_text_16,
            "small_text_18": doc.small_text_18,
            "potential": doc.potential,
            "performance": doc.performance,
            "promotion": doc.promotion,
            "any_other_observations": doc.any_other_observations,
            "potential_hod": doc.potential_hod,
            "performance_hod": doc.performance_hod,
            "promotion_hod": doc.promotion_hod,
            "any_other_observations_hod": doc.any_other_observations_hod,
            "required__job_knowledge": doc.required__job_knowledge,
            "training_required_to_enhance_job_knowledge": doc.training_required_to_enhance_job_knowledge,
            "required_skills": doc.required_skills,
            "training_required__to_enhance_skills_competencies": doc.training_required__to_enhance_skills_competencies
        })
        epmm.set('sales_target', [])
        child = doc.sales_target
        for c in child:
            epmm.append("sales_target",{
                "year": c.year,
                "actual_targets": c.actual_targets,
                "attained_targets": c.attained_targets,
                "order_booked":c.order_booked

            })
        epmm.set('job_analysis', [])
        child1 = doc.job_analysis
        for c in child1:
            epmm.append("job_analysis",{
                "appraisee_remarks": c.appraisee_remarks,
                "appraiser_remarks": c.appraiser_remarks
            })
        epmm.set('competency_assessment1', [])
        child2 = doc.competency_assessment1
        for c in child2:
            epmm.append("competency_assessment1",{
                "competency": c.competency,
                "weightage": c.weightage,
                "appraisee_weightage": c.appraisee_weightage,
                "appraiser_rating": c.manager,
                "hod": c.hod,
                "reviewer": c.hod
            })
        epmm.set('key_result_area', [])
        child3 = doc.key_result_area
        for c in child3:
            if c.reviewer:
                epmm.append("key_result_area",{
                    "goal_setting_for_current_year": c.goal_setting_for_current_year,
                    "performance_measure": c.performance_measure,
                    "weightage_w_100": c.weightage_w_100,
                    "weightage": c.weightage,
                    "self_rating": c.self_rating,
                    "appraiser_rating_r": c.manager,
                    "hod": c.hod,
                    "reviewer": c.reviewer
                })
            else:
                epmm.append("key_result_area",{
                    "goal_setting_for_current_year": c.goal_setting_for_current_year,
                    "performance_measure": c.performance_measure,
                    "weightage_w_100": c.weightage_w_100,
                    "weightage": c.weightage,
                    "self_rating": c.self_rating,
                    "appraiser_rating_r": c.manager,
                    "hod": c.hod,
                    "reviewer": c.hod
                })
        epmm.set('key_results_area', [])
        child4 = doc.key_results_area
        for c in child4:
            epmm.append("key_results_area",{
                "goal_setting_for_last_year": c.goal_setting_for_last_year,
                "performance_measure": c.performance_measure,
                "weightage_w_100": c.weightage_w_100,
                "weighted_score": c.weightage,
            })
        epmm.set('employee_feedback', [])
        child5 = doc.employee_feedback
        for c in child5:
            epmm.append("employee_feedback",{
                "appraisee_remarks": c.appraisee_remarks,
                "hod": c.hod
            })
        pm = frappe.db.exists("Performance Management Reviewer",{"employee_code": doc.employee_code,"appraisal_year":(cint(doc.appraisal_year) - 1)})
        if pm:
            employeedoc = frappe.get_doc("Performance Management Reviewer",pm)
            if employeedoc:
                epmm.set('management_pm_details', [])
                child6 = employeedoc.management_pm_details
                for c in child6:
                    epmm.append("management_pm_details",{
                        "year": c.year,
                        "hike": c.hike
                    })
        else:
            employee_appraisal_info = frappe.db.exists("Employee",{"name": doc.employee_code})
            if employee_appraisal_info:
                employeedoc = frappe.get_doc("Employee",employee_appraisal_info)
                if employeedoc:
                    epmm.set('management_pm_details', [])
                    child6 = employeedoc.pm_appraisal_info
                    for c in child6:
                        epmm.append("management_pm_details",{
                            "year": c.year,
                            "hike": c.hike
                        })
        epmm.save(ignore_permissions=True)

@frappe.whitelist()
def update_self_to_manager():
    self_list = ["PMS0470"]
    for s in self_list:
        doc = frappe.get_doc("Performance Management Self", s)
        # if doc.manager:
        pmm = frappe.db.get_value("Performance Management Manager", {
                                    "employee_code": doc.employee_code,"appraisal_year":doc.appraisal_year})
        if pmm:
            epmm = frappe.get_doc("Performance Management Manager", pmm)
        else:
            epmm = frappe.new_doc("Performance Management Manager")
        epmm.update({
            "employee_code": doc.employee_code,
            "employee_code1": doc.employee_code,
            "cost_code": doc.cost_code,
            "department": doc.department,
            "year_of_last_promotion": doc.year_of_last_promotion,
            "business_unit": doc.business_unit,
            "grade": doc.grade,
            "employee_name": doc.employee_name,
            "manager": doc.manager,
            "hod": doc.hod,
            "reviewer": doc.reviewer,
            "designation": doc.designation,
            "date_of_joining": doc.date_of_joining,
            "appraisal_year": doc.appraisal_year,
            "location": doc.location,
            "out_experience":doc.in_experience,
            "hdi_experience":doc.hd_experience,
            "total_experience":doc.total_experience,
            "no_of_promotion": doc.no_of_promotion,
            "small_text_12": doc.small_text_12,
            "small_text_14": doc.small_text_14,
            "small_text_16": doc.small_text_16,
            "small_text_18": doc.small_text_18,
            "required__job_knowledge": doc.required__job_knowledge,
            "training_required_to_enhance_job_knowledge": doc.training_required_to_enhance_job_knowledge,
            "required_skills": doc.required_skills,
            "training_required__to_enhance_skills_competencies": doc.training_required__to_enhance_skills_competencies
        })
        epmm.set('sales_target', [])
        child = doc.sales_target
        for c in child:
            epmm.append("sales_target",{
                "year": c.year,
                "actual_targets": c.actual_targets,
                "attained_targets": c.attained_targets
            })
        epmm.set('job_analysis', [])
        child1 = doc.job_analysis
        for c in child1:
            epmm.append("job_analysis",{
                "appraisee_remarks": c.appraisee_remarks
            })
        epmm.set('competency_assessment1', [])
        child2 = doc.competency_assessment1
        for c in child2:
            epmm.append("competency_assessment1",{
                "competency": c.competency,
                "weightage": c.weightage,
                "appraisee_weightage": c.appraisee_weightage,
                "manager": c.appraisee_weightage
            })
        epmm.set('key_result_area', [])
        child3 = doc.key_result_area
        for c in child3:
            epmm.append("key_result_area",{
                "goal_setting_for_current_year": c.goal_setting_for_current_year,
                "performance_measure": c.performance_measure,
                "weightage_w_100": c.weightage_w_100,
                "self_rating": c.self_rating,
                "manager": c.self_rating,
                "weightage": c.weightage,
            })
        epmm.set('key_results_area', [])
        child4 = doc.key_results_area
        for c in child4:
            epmm.append("key_results_area",{
                "goal_setting_for_last_year": c.goal_setting_for_last_year,
                "performance_measure": c.performance_measure,
                "weightage_w_100": c.weightage_w_100,
                "self_rating": c.self_rating,
                "weightage": c.weightage,
            })
        epmm.save(ignore_permissions=True)
    else:
        pmm = frappe.db.get_value("Performance Management HOD", {
                                    "employee_code": doc.employee_code,"appraisal_year":doc.appraisal_year})
        if pmm:
            epmm = frappe.get_doc("Performance Management HOD", pmm)
        else:
            epmm = frappe.new_doc("Performance Management HOD")
        epmm.update({
            "employee_code": doc.employee_code,
            "employee_code1": doc.employee_code,
            "cost_code": doc.cost_code,
            "department": doc.department,
            "year_of_last_promotion": doc.year_of_last_promotion,
            "business_unit": doc.business_unit,
            "grade": doc.grade,
            "employee_name": doc.employee_name,
            "manager": doc.manager,
            "hod": doc.hod,
            "reviewer": doc.reviewer,
            "designation": doc.designation,
            "date_of_joining": doc.date_of_joining,
            "appraisal_year": doc.appraisal_year,
            "location": doc.location,
            "out_experience":doc.in_experience,
            "hdi_experience":doc.hd_experience,
            "total_experience":doc.total_experience,
            "no_of_promotion": doc.no_of_promotion,
            "small_text_12": doc.small_text_12,
            "small_text_14": doc.small_text_14,
            "small_text_16": doc.small_text_16,
            "small_text_18": doc.small_text_18,
            "potential": "-",
            "performance": "-",
            "promotion": "-",
            "any_other_observations": "-",
            "required__job_knowledge": doc.required__job_knowledge,
            "training_required_to_enhance_job_knowledge": doc.training_required_to_enhance_job_knowledge,
            "required_skills": doc.required_skills,
            "training_required__to_enhance_skills_competencies": doc.training_required__to_enhance_skills_competencies
        })
        epmm.set('sales_target', [])
        child = doc.sales_target
        for c in child:
            epmm.append("sales_target",{
                "year": c.year,
                "actual_targets": c.actual_targets,
                "attained_targets": c.attained_targets
            })
        epmm.set('job_analysis', [])
        child1 = doc.job_analysis
        for c in child1:
            epmm.append("job_analysis",{
                "appraisee_remarks": c.appraisee_remarks,
                "appraiser_remarks": "-"
            })
        epmm.set('competency_assessment1', [])
        child2 = doc.competency_assessment1
        for c in child2:
            epmm.append("competency_assessment1",{
                "competency": c.competency,
                "weightage": c.weightage,
                "appraisee_weightage": c.appraisee_weightage,
                "manager": "-",
                "hod": c.appraisee_weightage
            })
        epmm.set('key_result_area', [])
        child3 = doc.key_result_area
        for c in child3:
            epmm.append("key_result_area",{
                "goal_setting_for_current_year": c.goal_setting_for_current_year,
                "performance_measure": c.performance_measure,
                "weightage_w_100": c.weightage_w_100,
                "self_rating": c.self_rating,
                "weightage": c.weightage,
                "manager": "-",
                "hod": c.self_rating
            })
        epmm.set('key_results_area', [])
        child4 = doc.key_results_area
        for c in child4:
            epmm.append("key_results_area",{
                "goal_setting_for_last_year": c.goal_setting_for_last_year,
                "performance_measure": c.performance_measure,
                "weightage_w_100": c.weightage_w_100,
                "weightage": c.weightage,
                "self_rating": c.self_rating
            })
        epmm.set('employee_feedback', [])
        # child5 = doc.employee_feedback
        for c in range(5):
            epmm.append("employee_feedback",{
                "appraisee_remarks": "-"
            })
        epmm.save(ignore_permissions=True)

@frappe.whitelist()
def update_hod():
    self_list = ["PMS0431"]
    for s in self_list:
        doc = frappe.get_doc("Performance Management Self", s)
        # if doc.docstatus == 1 and doc.manager:
        #     print('HI')
        pmm = frappe.db.get_value("Performance Management HOD", {
                                    "employee_code": doc.employee_code,"appraisal_year":doc.appraisal_year})
        if pmm:
            epmm = frappe.get_doc("Performance Management HOD", pmm)
        else:
            epmm = frappe.new_doc("Performance Management HOD")
        epmm.update({
            "employee_code": doc.employee_code,
            "cost_code": doc.cost_code,
            "department": doc.department,
            "year_of_last_promotion": doc.year_of_last_promotion,
            "business_unit": doc.business_unit,
            "grade": doc.grade,
            "employee_name": doc.employee_name,
            "manager": doc.manager,
            "hod": doc.hod,
            "reviewer": doc.reviewer,
            "designation": doc.designation,
            "date_of_joining": doc.date_of_joining,
            "appraisal_year": doc.appraisal_year,
            "location": doc.location,
            "out_experience":doc.in_experience,
            "hdi_experience":doc.hd_experience,
            "total_experience":doc.total_experience,
            "no_of_promotion": doc.no_of_promotion,
            "small_text_12": doc.small_text_12,
            "small_text_14": doc.small_text_14,
            "small_text_16": doc.small_text_16,
            "small_text_18": doc.small_text_18,
            "potential": "-",
            "performance": "-",
            "promotion": "-",
            "any_other_observations": "-",
            "required__job_knowledge": doc.required__job_knowledge,
            "training_required_to_enhance_job_knowledge": doc.training_required_to_enhance_job_knowledge,
            "required_skills": doc.required_skills,
            "training_required__to_enhance_skills_competencies": doc.training_required__to_enhance_skills_competencies
        })
        epmm.set('sales_target', [])
        child = doc.sales_target
        for c in child:
            epmm.append("sales_target",{
                "year": c.year,
                "actual_targets": c.actual_targets,
                "attained_targets": c.attained_targets
            })
        epmm.set('job_analysis', [])
        child1 = doc.job_analysis
        for c in child1:
            epmm.append("job_analysis",{
                "appraisee_remarks": c.appraisee_remarks,
                "appraiser_remarks": "-"
            })
        epmm.set('competency_assessment1', [])
        child2 = doc.competency_assessment1
        for c in child2:
            epmm.append("competency_assessment1",{
                "competency": c.competency,
                "weightage": c.weightage,
                "appraisee_weightage": c.appraisee_weightage,
                "manager": "-",
                "hod": c.appraisee_weightage
            })
        epmm.set('key_result_area', [])
        child3 = doc.key_result_area
        for c in child3:
            epmm.append("key_result_area",{
                "goal_setting_for_current_year": c.goal_setting_for_current_year,
                "performance_measure": c.performance_measure,
                "weightage_w_100": c.weightage_w_100,
                "self_rating": c.self_rating,
                "weightage": c.weightage,
                "manager": "-",
                "hod": c.self_rating
            })
        epmm.set('key_results_area', [])
        child4 = doc.key_results_area
        for c in child4:
            epmm.append("key_results_area",{
                "goal_setting_for_last_year": c.goal_setting_for_last_year,
                "performance_measure": c.performance_measure,
                "weightage_w_100": c.weightage_w_100,
                "weightage": c.weightage,
                "self_rating": c.self_rating
            })
        epmm.set('employee_feedback', [])
        # child5 = doc.employee_feedback
        for c in range(5):
            epmm.append("employee_feedback",{
                "appraisee_remarks": "-"
            })
        epmm.save(ignore_permissions=True)
        frappe.db.commit()

@frappe.whitelist()
def update_self_to_reviewer():
    self_list = ["PMS0513"]
    for s in self_list:
        doc = frappe.get_doc("Performance Management Self", s)
        # if doc.docstatus == 1 and doc.manager:
        #     print('HI')
        pmr = frappe.db.get_value("Performance Management Reviewer", {
                                    "employee_code": doc.employee_code,"appraisal_year":doc.appraisal_year})
        if pmr:
            epmr = frappe.get_doc("Performance Management Reviewer", pmr)
        else:
            epmr = frappe.new_doc("Performance Management Reviewer")
        epmr.update({
            "employee_code": doc.employee_code,
            "cost_code": doc.cost_code,
            "department": doc.department,
            "year_of_last_promotion": doc.year_of_last_promotion,
            "business_unit": doc.business_unit,
            "grade": doc.grade,
            "employee_name": doc.employee_name,
            # "manager": doc.manager,
            # "hod": doc.hod,
            "reviewer": doc.reviewer,
            "designation": doc.designation,
            "date_of_joining": doc.date_of_joining,
            "appraisal_year": doc.appraisal_year,
            "location": doc.location,
            "out_experience":doc.in_experience,
            "hdi_experience":doc.hd_experience,
            "total_experience":doc.total_experience,
            "no_of_promotion": doc.no_of_promotion,
            "small_text_12": doc.small_text_12,
            "small_text_14": doc.small_text_14,
            "small_text_16": doc.small_text_16,
            "small_text_18": doc.small_text_18,
            "potential": "-",
            "performance": "-",
            "promotion": "-",
            "any_other_observations": "-",
            "potential_hod": "-",
            "performance_hod": "-",
            "promotion_hod": "-",
            "any_other_observations_hod": "-",
            "required__job_knowledge": doc.required__job_knowledge,
            "training_required_to_enhance_job_knowledge": doc.training_required_to_enhance_job_knowledge,
            "required_skills": doc.required_skills,
            "training_required__to_enhance_skills_competencies": doc.training_required__to_enhance_skills_competencies
        })
        epmr.set('sales_target', [])
        child = doc.sales_target
        for c in child:
            epmr.append("sales_target",{
                "year": c.year,
                "actual_targets": c.actual_targets,
                "attained_targets": c.attained_targets,
                "order_booked": c.order_booked
            })
        epmr.set('job_analysis', [])
        child1 = doc.job_analysis
        for c in child1:
            epmr.append("job_analysis",{
                "appraisee_remarks": c.appraisee_remarks,
                "appraiser_remarks": "-"
            })
        epmr.set('competency_assessment1', [])
        child2 = doc.competency_assessment1
        for c in child2:
            epmr.append("competency_assessment1",{
                "competency": c.competency,
                "weightage": c.weightage,
                "appraisee_weightage": c.appraisee_weightage,
                "appraiser_rating": "-",
                "hod": "-",
                "reviewer": c.appraisee_weightage,
            })
        epmr.set('key_result_area', [])
        child3 = doc.key_result_area
        for c in child3:
            epmr.append("key_result_area",{
                "goal_setting_for_current_year": c.goal_setting_for_current_year,
                "performance_measure": c.performance_measure,
                "weightage_w_100": c.weightage_w_100,
                "self_rating": c.self_rating,
                "weightage": c.weightage,
                "appraiser_rating_r": "-",
                "hod": "-",
                "reviewer": c.self_rating,
            })
        epmr.set('key_results_area', [])
        child4 = doc.key_results_area
        for c in child4:
            epmr.append("key_results_area",{
                "goal_setting_for_last_year": c.goal_setting_for_last_year,
                "performance_measure": c.performance_measure,
                "weightage_w_100": c.weightage_w_100,
                "weightage": c.weightage,
                "self_rating": c.self_rating
            })
        epmr.set('employee_feedback', [])
        # child5 = doc.employee_feedback
        for c in range(5):
            epmr.append("employee_feedback",{
                "appraisee_remarks": "-",
                "hod":"-"
            })
        employee_appraisal_info = frappe.db.exists("Employee",{"name": doc.employee_code})
        if employee_appraisal_info:
            employeedoc = frappe.get_doc("Employee",employee_appraisal_info)
            if employeedoc:
                epmr.set('management_pm_details', [])
                child6 = employeedoc.pm_appraisal_info
                for c in child6:
                    epmr.append("management_pm_details",{
                        "year": c.year,
                        "hike": c.hike
                    })
        epmr.save(ignore_permissions=True)
        frappe.db.commit()

@frappe.whitelist()
def update_pm_calibration(doc,method):
    if doc.name:
        pmc = frappe.db.get_value("Performance Management Calibration", {
                                      "employee_code": doc.employee_code,"appraisal_year":doc.appraisal_year})
        if pmc:
            epmc = frappe.get_doc("Performance Management Calibration", pmc)
        else:
            epmc = frappe.new_doc("Performance Management Calibration")
        epmc.update({
            "competency_assessment": doc.average_score_attained,
            "goal_setting_2018": doc.average_score,
            "potential": doc.potential_reviewer,
            "performance": doc.performance_reviewer,
            "promotion": doc.promotion_reviewer,
            "any_other_observations": doc.any_other_observations_reviewer,
            "increment": doc.increment,
            "remarks": doc.remarks,
            "salary_correction": doc.salary_correction,
        })
        epmc.save(ignore_permissions=True)
        epmc.db.commit()

        # pmm = frappe.db.get_value("Individual Performance", {
        #                               "employee_code": doc.employee_code})
        # if pmm:
        #     epmm = frappe.get_doc("Individual Performance", pmm)
        # else:
        #     epmm = frappe.new_doc("Individual Performance")
        # epmm.update({
        #     "employee_code": doc.employee_code,
        #     "employee_code1": doc.employee_code,
        #     "cost_code": doc.cost_code,
        #     "department": doc.department,
        #     "year_of_last_promotion": doc.year_of_last_promotion,
        #     "business_unit": doc.business_unit,
        #     "grade": doc.grade,
        #     "employee_name": doc.employee_name,
        #     "manager": doc.manager,
        #     "hod": doc.hod,
        #     "reviewer": doc.reviewer,
        #     "designation": doc.designation,
        #     "date_of_joining": doc.date_of_joining,
        #     "appraisal_year": doc.appraisal_year,
        #     "location": doc.location,
        #     "no_of_promotion": doc.no_of_promotion,
        #     "small_text_12": doc.small_text_12,
        #     "small_text_14": doc.small_text_14,
        #     "small_text_16": doc.small_text_16,
        #     "small_text_18": doc.small_text_18,
        #     "potential": doc.potential,
        #     "performance": doc.performance,
        #     "promotion": doc.promotion,
        #     "any_other_observations": doc.any_other_observations,
        #     "potential_hod": doc.potential_hod,
        #     "performance_hod": doc.performance_hod,
        #     "promotion_hod": doc.promotion_hod,
        #     "any_other_observations_hod": doc.any_other_observations_hod,
        #     "required__job_knowledge": doc.required__job_knowledge,
        #     "training_required_to_enhance_job_knowledge": doc.training_required_to_enhance_job_knowledge,
        #     "required_skills": doc.required_skills,
        #     "training_required__to_enhance_skills_competencies": doc.training_required__to_enhance_skills_competencies
        # })
        # epmm.set('sales_target', [])
        # child = doc.sales_target
        # for c in child:
        #     epmm.append("sales_target",{
        #         "year": c.year,
        #         "actual_targets": c.actual_targets,
        #         "attained_targets": c.attained_targets
        #     })
        # # epmm.set('job_analysis', [])
        # # child1 = doc.job_analysis
        # # for c in child1:
        # #     epmm.append("job_analysis",{
        # #         "appraisee_remarks": c.appraisee_remarks,
        # #         "appraiser_remarks": c.appraiser_remarks
        # #     })
        # epmm.set('competency_assessment1', [])
        # child2 = doc.competency_assessment1
        # for c in child2:
        #     epmm.append("competency_assessment1",{
        #         "competency": c.competency,
        #         "weightage": c.weightage,
        #         "appraisee_weightage": c.appraisee_weightage,
        #         "reviewer": c.reviewer
        #     })
        # epmm.set('key_result_area', [])
        # child3 = doc.key_result_area
        # for c in child3:
        #     epmm.append("key_result_area",{
        #         "goal_setting_for_current_year": c.goal_setting_for_current_year,
        #         "performance_measure": c.performance_measure,
        #         "weightage_w_100": c.weightage_w_100,
        #         "weightage": c.weightage,
        #         "self_rating": c.self_rating,
        #         "reviewer": c.reviewer
        #     })
        # epmm.set('key_results_area', [])
        # child4 = doc.key_results_area
        # for c in child4:
        #     epmm.append("key_results_area",{
        #         "goal_setting_for_last_year": c.goal_setting_for_last_year,
        #         "performance_measure": c.performance_measure,
        #         "weightage_w_100": c.weightage_w_100,
        #     })
        # epmm.set('employee_feedback', [])
        # child5 = doc.employee_feedback
        # for c in child5:
        #     epmm.append("employee_feedback",{
        #         "appraisee_remarks": c.appraisee_remarks,
        #         "hod": c.hod,
        #         "appraiser_remarks": c.appraiser_remarks
        #     })
        # epmm.save(ignore_permissions=True)

@frappe.whitelist()
def manually_update_pm_calibration_previous_increment():
    current_year = '2022'
    previous_year = '2021'
    docs = frappe.db.get_list("Performance Management Calibration",{"appraisal_year":current_year})
    for d in docs:
        pmc_cy = frappe.get_doc("Performance Management Calibration",d.name)
        if pmc_cy.name:
            previous_year_pmc = frappe.db.get_value("Performance Management Calibration", {
                                        "employee_code": pmc_cy.employee_code,"appraisal_year":previous_year})
            if previous_year_pmc:
                pmc_ly = frappe.get_doc("Performance Management Calibration", previous_year_pmc)
                pmc_cy.update({
                    "basic_ly": pmc_ly.basic,
                    "hra_ly": pmc_ly.hra,
                    "special_allowance_ly": pmc_ly.special_allowance,
                    "transport_ly": pmc_ly.transport,
                    "education_ly": pmc_ly.education,
                    "food_allowance_ly": pmc_ly.food_allowance,
                    "relocation_allowance_ly": pmc_ly.relocation_allowance,
                    "washing_allowance_ly": pmc_ly.washing_allowance,
                    "site_allowance_ly": pmc_ly.site_allowance,
                    "car_allowance_ly": pmc_ly.car_allowance,
                    "pf_contribution_ly": pmc_ly.pf_contribution,
                    "esi_ly": pmc_ly.esi,
                    "monthly_gross_ly": pmc_ly.new_monthly_gross,
                    "driver_salary_ly": pmc_ly.driver_salary,
                    "car_emi_ly": pmc_ly.car_emi,
                    "lta_ly": pmc_ly.lta,
                    "gratuity_ly": pmc_ly.gratuity,
                    "exgratia_ly":pmc_ly.exgratia,
                    "sales_project_support_incentive_ly": pmc_ly.sales_project_support_incentive,
                    "performance_incentive_ly": pmc_ly.performance_incentive,
                    "annual_ctc_ly": pmc_ly.new_annual_ctc
                })
                pmc_cy.save(ignore_permissions=True)



@frappe.whitelist()
def manually_update_pm_calibration():
    # if frappe.db.exists("Performance Management Reviewer",{"docstatus": 1}):
    # docs = frappe.db.get_all("Performance Management Reviewer",{"docstatus": 1,"appraisal_year":"2022"})
    docs = frappe.db.sql("""select * from `tabPerformance Management Reviewer` where employee_code1 != '' and docstatus = 1 and appraisal_year = '2022' """,as_dict =1)
    for d in docs:
        doc = frappe.get_doc("Performance Management Reviewer",d.name)
        if doc.name:
            pmc = frappe.db.get_value("Performance Management Calibration", {
                                        "employee_code": doc.employee_code1,"appraisal_year":"2022"})
            if pmc:
                epmc = frappe.get_doc("Performance Management Calibration", pmc)
            else:
                epmc = frappe.new_doc("Performance Management Calibration")
            epmc.update({
                "employee_code": doc.employee_code1,
                "cost_code": doc.cost_code,
                "department": doc.department,
                "business_unit": doc.business_unit,
                "grade": doc.grade,
                "employee_name": doc.employee_name,
                "designation": doc.designation,
                "date_of_joining": doc.date_of_joining,
                "appraisal_year": doc.appraisal_year,
                "location": doc.location,
                "pm_year": datetime.now().year,
                "no_of_promotion": doc.no_of_promotion,
                "competency_assessment": doc.average_score_attained,
                "goal_setting_2018": doc.average_score, 
                "potential": doc.potential_reviewer,
                "performance": doc.performance_reviewer,
                "promotion": doc.promotion_reviewer,
                "any_other_observations": doc.any_other_observations_reviewer,
                "increment": doc.increment,
                "remarks": doc.remarks,
                "salary_correction": doc.salary_correction,
                "r_designation": doc.designation,
                "r_location": doc.location,
                "r_grade": doc.grade
            })
            epmc.set('management_pm_details', [])
            child = doc.management_pm_details
            for c in child:
                epmc.append("management_pm_details",{
                    "year": c.year,
                    "hike": c.hike
                })
            epmc.save(ignore_permissions=True)
            # epmc.db.commit()

            pmm = frappe.db.get_value("Individual Performance", {
                                        "employee_code": doc.employee_code,"appraisal_year":"2022"})
            if pmm:
                epmm = frappe.get_doc("Individual Performance", pmm)
            else:
                epmm = frappe.new_doc("Individual Performance")
            epmm.update({
                "employee_code": doc.employee_code,
                "employee_code1": doc.employee_code,
                "cost_code": doc.cost_code,
                "department": doc.department,
                "year_of_last_promotion": doc.year_of_last_promotion,
                "business_unit": doc.business_unit,
                "grade": doc.grade,
                "employee_name": doc.employee_name,
                "manager": doc.manager,
                "hod": doc.hod,
                "reviewer": doc.reviewer,
                "designation": doc.designation,
                "date_of_joining": doc.date_of_joining,
                "appraisal_year": doc.appraisal_year,
                "location": doc.location,
                "no_of_promotion": doc.no_of_promotion,
                "small_text_12": doc.small_text_12,
                "small_text_14": doc.small_text_14,
                "small_text_16": doc.small_text_16,
                "small_text_18": doc.small_text_18,
                "potential": doc.potential,
                "performance": doc.performance,
                "promotion": doc.promotion,
                "any_other_observations": doc.any_other_observations,
                "potential_hod": doc.potential_hod,
                "performance_hod": doc.performance_hod,
                "promotion_hod": doc.promotion_hod,
                "any_other_observations_hod": doc.any_other_observations_hod,
                "required__job_knowledge": doc.required__job_knowledge,
                "training_required_to_enhance_job_knowledge": doc.training_required_to_enhance_job_knowledge,
                "required_skills": doc.required_skills,
                "pm_year": datetime.now().year,
                "training_required__to_enhance_skills_competencies": doc.training_required__to_enhance_skills_competencies
            })
            epmm.set('sales_target', [])
            child = doc.sales_target
            for c in child:
                epmm.append("sales_target",{
                    "year": c.year,
                    "actual_targets": c.actual_targets,
                    "attained_targets": c.attained_targets
                })
            # epmm.set('job_analysis', [])
            # child1 = doc.job_analysis
            # for c in child1:
            #     epmm.append("job_analysis",{
            #         "appraisee_remarks": c.appraisee_remarks,
            #         "appraiser_remarks": c.appraiser_remarks
            #     })
            epmm.set('competency_assessment1', [])
            child2 = doc.competency_assessment1
            for c in child2:
                epmm.append("competency_assessment1",{
                    "competency": c.competency,
                    "weightage": c.weightage,
                    "appraisee_weightage": c.appraisee_weightage,
                    "reviewer": c.reviewer
                })
            epmm.set('key_result_area', [])
            child3 = doc.key_result_area
            for c in child3:
                epmm.append("key_result_area",{
                    "goal_setting_for_current_year": c.goal_setting_for_current_year,
                    "performance_measure": c.performance_measure,
                    "weightage_w_100": c.weightage_w_100,
                    "weightage": c.weightage,
                    "self_rating": c.self_rating,
                    "reviewer": c.reviewer
                })
            epmm.set('key_results_area', [])
            child4 = doc.key_results_area
            for c in child4:
                epmm.append("key_results_area",{
                    "goal_setting_for_last_year": c.goal_setting_for_last_year,
                    "performance_measure": c.performance_measure,
                    "weightage_w_100": c.weightage_w_100,
                })
            epmm.set('employee_feedback', [])
            child5 = doc.employee_feedback
            for c in child5:
                epmm.append("employee_feedback",{
                    "appraisee_remarks": c.appraisee_remarks,
                    "hod": c.hod,
                    "appraiser_remarks": c.appraiser_remarks
                })
            epmm.save(ignore_permissions=True)


@frappe.whitelist()
def update_pm_hod_doc():
    manager_list = ["PMM0277"]
    for m in manager_list:
        doc = frappe.get_doc("Performance Management Manager", m)
    # doc = frappe.get_doc("Performance Management Manager", {"employee_code": "1204"})
        pmm = frappe.db.get_value("Performance Management HOD", {
                                    "employee_code": doc.employee_code,"appraisal_year":doc.appraisal_year})
        if pmm:
            epmm = frappe.get_doc("Performance Management HOD", pmm)
        else:
            epmm = frappe.new_doc("Performance Management HOD")
        epmm.update({
            "employee_code": doc.employee_code,
            "employee_code1": doc.employee_code,
            "cost_code": doc.cost_code,
            "department": doc.department,
            "year_of_last_promotion": doc.year_of_last_promotion,
            "business_unit": doc.business_unit,
            "grade": doc.grade,
            "employee_name": doc.employee_name,
            "manager": doc.manager,
            "hod": doc.hod,
            "reviewer": doc.reviewer,
            "designation": doc.designation,
            "date_of_joining": doc.date_of_joining,
            "appraisal_year": doc.appraisal_year,
            "location": doc.location,
            "out_experience":doc.in_experience,
            "hdi_experience":doc.hd_experience,
            "total_experience":doc.total_experience,
            "no_of_promotion": doc.no_of_promotion,
            "small_text_12": doc.small_text_12,
            "small_text_14": doc.small_text_14,
            "small_text_16": doc.small_text_16,
            "small_text_18": doc.small_text_18,
            "potential": doc.potential,
            "performance": doc.performance,
            "promotion": doc.promotion,
            "any_other_observations": doc.any_other_observations,
            "required__job_knowledge": doc.required__job_knowledge,
            "training_required_to_enhance_job_knowledge": doc.training_required_to_enhance_job_knowledge,
            "required_skills": doc.required_skills,
            "training_required__to_enhance_skills_competencies": doc.training_required__to_enhance_skills_competencies
        })
        epmm.set('sales_target', [])
        child = doc.sales_target
        for c in child:
            epmm.append("sales_target",{
                "year": c.year,
                "actual_targets": c.actual_targets,
                "attained_targets": c.attained_targets
            })
        epmm.set('job_analysis', [])
        child1 = doc.job_analysis
        for c in child1:
            epmm.append("job_analysis",{
                "appraisee_remarks": c.appraisee_remarks,
                "appraiser_remarks": c.appraiser_remarks
            })
        epmm.set('competency_assessment1', [])
        child2 = doc.competency_assessment1
        for c in child2:
            epmm.append("competency_assessment1",{
                "competency": c.competency,
                "weightage": c.weightage,
                "appraisee_weightage": c.appraisee_weightage,
                "manager": c.manager,
                "hod": c.manager
            })
        epmm.set('key_result_area', [])
        child3 = doc.key_result_area
        for c in child3:
            epmm.append("key_result_area",{
                "goal_setting_for_current_year": c.goal_setting_for_current_year,
                "performance_measure": c.performance_measure,
                "weightage_w_100": c.weightage_w_100,
                "self_rating": c.self_rating,
                "weightage": c.weightage,
                "manager": c.manager,
                "hod": c.manager
            })
        epmm.set('key_results_area', [])
        child4 = doc.key_results_area
        for c in child4:
            epmm.append("key_results_area",{
                "goal_setting_for_last_year": c.goal_setting_for_last_year,
                "performance_measure": c.performance_measure,
                "weightage_w_100": c.weightage_w_100,
                "weightage": c.weightage,
                "self_rating": c.self_rating
            })
        epmm.set('employee_feedback', [])
        child5 = doc.employee_feedback
        for c in child5:
            epmm.append("employee_feedback",{
                "appraisee_remarks": c.appraisee_remarks
            })
        epmm.save(ignore_permissions=True)                        