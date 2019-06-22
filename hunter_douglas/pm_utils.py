@frappe.whitelist()
def update_pm_manager(doc, method):
    if doc.manager:
        pmm = frappe.db.get_value("Performance Management Manager", {
                                      "employee_code": doc.employee_code})
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
                                      "employee_code": doc.employee_code})
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
            "no_of_promotion": doc.no_of_promotion,
            "small_text_12": doc.small_text_12,
            "small_text_14": doc.small_text_14,
            "small_text_16": doc.small_text_16,
            "small_text_18": doc.small_text_18,
            "potential": "NA",
            "performance": "NA",
            "promotion": "NA",
            "any_other_observations": "NA",
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
                "appraiser_remarks": "NA"
            })
        epmm.set('competency_assessment1', [])
        child2 = doc.competency_assessment1
        for c in child2:
            epmm.append("competency_assessment1",{
                "competency": c.competency,
                "weightage": c.weightage,
                "appraisee_weightage": c.appraisee_weightage,
                "manager": "NA",
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
                "manager": "NA",
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
                "appraisee_remarks": "NA"
            })
        epmm.save(ignore_permissions=True)



@frappe.whitelist()
def update_pm_hod(doc, method):
    if doc.manager == frappe.session.user:
        pmm = frappe.db.get_value("Performance Management HOD", {
                                      "employee_code": doc.employee_code})
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
        



@frappe.whitelist()
def update_pm_reviewer(doc, method):
    if doc.hod:
        pmm = frappe.db.get_value("Performance Management Reviewer", {
                                        "employee_code": doc.employee_code})
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
                "appraiser_rating": c.manager,
                "hod": c.hod,
                "reviewer": c.hod
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
            })
        epmm.set('employee_feedback', [])
        child5 = doc.employee_feedback
        for c in child5:
            epmm.append("employee_feedback",{
                "appraisee_remarks": c.appraisee_remarks,
                "hod": c.hod
            })
        employeedoc = frappe.get_doc("Employee",doc.employee_code)
        if employeedoc:
            epmm.set('management_pm_details', [])
            child6 = employeedoc.management_pm_details
            for c in child6:
                epmm.append("management_pm_details",{
                    "year": c.year,
                    "hike": c.hike
                })
        epmm.save(ignore_permissions=True)

@frappe.whitelist()
def update_hod():
    self_list = ["PMS0085"]
    for s in self_list:
        doc = frappe.get_doc("Performance Management Self", s)
        if doc.docstatus == 1 and doc.manager:
            pmm = frappe.db.get_value("Performance Management HOD", {
                                        "employee_code": doc.employee_code})
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
                "no_of_promotion": doc.no_of_promotion,
                "small_text_12": doc.small_text_12,
                "small_text_14": doc.small_text_14,
                "small_text_16": doc.small_text_16,
                "small_text_18": doc.small_text_18,
                "potential": "NA",
                "performance": "NA",
                "promotion": "NA",
                "any_other_observations": "NA",
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
                    "appraiser_remarks": "NA"
                })
            epmm.set('competency_assessment1', [])
            child2 = doc.competency_assessment1
            for c in child2:
                epmm.append("competency_assessment1",{
                    "competency": c.competency,
                    "weightage": c.weightage,
                    "appraisee_weightage": c.appraisee_weightage,
                    "manager": "NA",
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
                    "manager": "NA",
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
                    "appraisee_remarks": "NA"
                })
            epmm.save(ignore_permissions=True)
            frappe.db.commit()


@frappe.whitelist()
def update_pm_calibration(doc,method):
    if doc.name:
        pmc = frappe.db.get_value("Performance Management Calibration", {
                                      "employee_code": doc.employee_code})
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
def manually_update_pm_calibration():
    # if frappe.db.exists("Performance Management Reviewer",{"docstatus": 1}):
    docs = frappe.db.get_list("Performance Management Reviewer",{"docstatus": 1})
    for d in docs:
        doc = frappe.get_doc("Performance Management Reviewer",d.name)
        if doc.name:
            pmc = frappe.db.get_value("Performance Management Calibration", {
                                        "employee_code": doc.employee_code1})
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
                                        "employee_code": doc.employee_code})
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


# @frappe.whitelist()
# def update_pm_hod_doc():
#     doc = frappe.get_doc("Performance Management Manager", {"employee_code": "1204"})
#     pmm = frappe.db.get_value("Performance Management HOD", {
#                                     "employee_code": doc.employee_code})
#     if pmm:
#         epmm = frappe.get_doc("Performance Management HOD", pmm)
#     else:
#         epmm = frappe.new_doc("Performance Management HOD")
#     epmm.update({
#         "employee_code": doc.employee_code,
#         "employee_code1": doc.employee_code,
#         "cost_code": doc.cost_code,
#         "department": doc.department,
#         "year_of_last_promotion": doc.year_of_last_promotion,
#         "business_unit": doc.business_unit,
#         "grade": doc.grade,
#         "employee_name": doc.employee_name,
#         "manager": doc.manager,
#         "hod": doc.hod,
#         "reviewer": doc.reviewer,
#         "designation": doc.designation,
#         "date_of_joining": doc.date_of_joining,
#         "appraisal_year": doc.appraisal_year,
#         "location": doc.location,
#         "no_of_promotion": doc.no_of_promotion,
#         "small_text_12": doc.small_text_12,
#         "small_text_14": doc.small_text_14,
#         "small_text_16": doc.small_text_16,
#         "small_text_18": doc.small_text_18,
#         "potential": doc.potential,
#         "performance": doc.performance,
#         "promotion": doc.promotion,
#         "any_other_observations": doc.any_other_observations,
#         "required__job_knowledge": doc.required__job_knowledge,
#         "training_required_to_enhance_job_knowledge": doc.training_required_to_enhance_job_knowledge,
#         "required_skills": doc.required_skills,
#         "training_required__to_enhance_skills_competencies": doc.training_required__to_enhance_skills_competencies
#     })
#     epmm.set('sales_target', [])
#     child = doc.sales_target
#     for c in child:
#         epmm.append("sales_target",{
#             "year": c.year,
#             "actual_targets": c.actual_targets,
#             "attained_targets": c.attained_targets
#         })
#     epmm.set('job_analysis', [])
#     child1 = doc.job_analysis
#     for c in child1:
#         epmm.append("job_analysis",{
#             "appraisee_remarks": c.appraisee_remarks,
#             "appraiser_remarks": c.appraiser_remarks
#         })
#     epmm.set('competency_assessment1', [])
#     child2 = doc.competency_assessment1
#     for c in child2:
#         epmm.append("competency_assessment1",{
#             "competency": c.competency,
#             "weightage": c.weightage,
#             "appraisee_weightage": c.appraisee_weightage,
#             "manager": c.manager,
#             "hod": c.manager
#         })
#     epmm.set('key_result_area', [])
#     child3 = doc.key_result_area
#     for c in child3:
#         epmm.append("key_result_area",{
#             "goal_setting_for_current_year": c.goal_setting_for_current_year,
#             "performance_measure": c.performance_measure,
#             "weightage_w_100": c.weightage_w_100,
#             "self_rating": c.self_rating,
#             "weightage": c.weightage,
#             "manager": c.manager,
#             "hod": c.manager
#         })
#     epmm.set('key_results_area', [])
#     child4 = doc.key_results_area
#     for c in child4:
#         epmm.append("key_results_area",{
#             "goal_setting_for_last_year": c.goal_setting_for_last_year,
#             "performance_measure": c.performance_measure,
#             "weightage_w_100": c.weightage_w_100,
#             "weightage": c.weightage,
#             "self_rating": c.self_rating
#         })
#     epmm.set('employee_feedback', [])
#     child5 = doc.employee_feedback
#     for c in child5:
#         epmm.append("employee_feedback",{
#             "appraisee_remarks": c.appraisee_remarks
#         })
#     epmm.save(ignore_permissions=True)                        