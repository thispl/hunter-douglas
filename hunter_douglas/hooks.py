# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "hunter_douglas"
app_title = "Hunter Douglas"
app_publisher = "VHRS"
app_description = "Custom App for Hunter Douglas"
app_icon = "octicon octicon-gear"
app_color = "grey"
app_email = "abdulla.pi@voltechgroup.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/hunter_douglas/css/hunter_douglas.css"
app_include_js = "/assets/hunter_douglas/js/mute_learn.js"

# include js, css files in header of web template
# web_include_css = "/assets/hunter_douglas/css/hunter_douglas.css"
# web_include_js = "/assets/hunter_douglas/js/hunter_douglas.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}
# on_login = "hunter_douglas.custom.send_birthday_wish"
# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }
update_website_context = "hunter_douglas.custom.update_website_context"
# Website user home page (by function)
# get_website_user_home_page = "hunter_douglas.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "hunter_douglas.install.before_install"
# after_install = "hunter_douglas.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "hunter_douglas.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Comp Off Balance":
    {
        "on_update": "hunter_douglas.custom.update_comp_off"
    },
    "Performance Management Self":
    {
        "on_submit": "hunter_douglas.custom.update_pm_manager"
    },
    "Performance Management Manager":
    {
        "on_submit": "hunter_douglas.custom.update_pm_hod"
    },
    "Performance Management HOD":
    {
        "on_submit": "hunter_douglas.custom.update_pm_reviewer"
    },
    # "Performance Management Reviewer":
    # {
    #     "on_submit": "hunter_douglas.custom.update_pm_calibration"
    # }
    # "On Duty Application":
    # {
    #     "on_submit": "hunter_douglas.hunter_douglas.doctype.on_duty_application.on_duty_application.on_duty_mark",
    # },
    "Travel Management":
    {
        "on_cancel": "hunter_douglas.hunter_douglas.doctype.travel_management.travel_management.delete_tour_application",
        # "on_submit": "hunter_douglas.hunter_douglas.doctype.travel_management.travel_management.send_ticket_copy",
    }
    # "*": {
    # 	"on_update": "method",
    # 	"on_cancel": "method",
    # 	"on_trash": "method"
    # }
}

# Scheduled Tasks
# ---------------

scheduler_events = {
# 	"all": [
# 		"hunter_douglas.tasks.all"
# 	],
    "daily": [
        "hunter_douglas.custom.fetch_att_prev"
    ],
    "cron": {
        "0 7-23/1 * * *":[
            "hunter_douglas.custom.fetch_att"
        ],
        "*/15 9-11 * * *":[
            "hunter_douglas.custom.fetch_att"
        ],
        # "0 5 25 * *":[
        #     "hunter_douglas.custom.calculate_comp_off"
        # ],
        # "00 10 * * *":[
        #     "hunter_douglas.custom.in_punch_alert"
        # ],
        "00 19 * * *":[
            "hunter_douglas.custom.fetch_att"
            "hunter_douglas.custom.out_punch_alert"
        ]
    }
# 	"weekly": [
# 		"hunter_douglas.tasks.weekly"
# 	]
# 	"monthly": [
# 		"hunter_douglas.tasks.monthly"
# 	]
}

# Testing
# -------

# before_tests = "hunter_douglas.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "hunter_douglas.event.get_events"
# }

