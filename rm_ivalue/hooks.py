app_name = "rm_ivalue"
app_title = "Rm Ivalue"
app_publisher = "Yazan Hamdan"
app_description = "a"
app_email = "yazan01mfh@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "rm_ivalue",
# 		"logo": "/assets/rm_ivalue/logo.png",
# 		"title": "Rm Ivalue",
# 		"route": "/rm_ivalue",
# 		"has_permission": "rm_ivalue.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/rm_ivalue/css/rm_ivalue.css"
# app_include_js = "/assets/rm_ivalue/js/rm_ivalue.js"

# include js, css files in header of web template
# web_include_css = "/assets/rm_ivalue/css/rm_ivalue.css"
# web_include_js = "/assets/rm_ivalue/js/rm_ivalue.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "rm_ivalue/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "rm_ivalue/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "rm_ivalue.utils.jinja_methods",
# 	"filters": "rm_ivalue.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "rm_ivalue.install.before_install"
# after_install = "rm_ivalue.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "rm_ivalue.uninstall.before_uninstall"
# after_uninstall = "rm_ivalue.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "rm_ivalue.utils.before_app_install"
# after_app_install = "rm_ivalue.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "rm_ivalue.utils.before_app_uninstall"
# after_app_uninstall = "rm_ivalue.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "rm_ivalue.notifications.get_notification_config"

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

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"rm_ivalue.tasks.all"
# 	],
# 	"daily": [
# 		"rm_ivalue.tasks.daily"
# 	],
# 	"hourly": [
# 		"rm_ivalue.tasks.hourly"
# 	],
# 	"weekly": [
# 		"rm_ivalue.tasks.weekly"
# 	],
# 	"monthly": [
# 		"rm_ivalue.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "rm_ivalue.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "rm_ivalue.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "rm_ivalue.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["rm_ivalue.utils.before_request"]
# after_request = ["rm_ivalue.utils.after_request"]

# Job Events
# ----------
# before_job = ["rm_ivalue.utils.before_job"]
# after_job = ["rm_ivalue.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"rm_ivalue.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True



"""
scheduler_events = {
    "daily": [
        "rm_ivalue.doctype.project_assignment.project_assignment.update_all_project_assignment_status"
    ]
}
"""

# Add this function to your project_assignment.py file:

@frappe.whitelist()
def update_all_project_assignment_status():
    """Update status for all submitted Project Assignments"""
    
    # Get all submitted project assignments
    assignments = frappe.get_all("Project Assignment", 
                                filters={"docstatus": 1},
                                fields=["name", "start_date", "end_date", "status"])
    
    today_date = getdate(today())
    
    for assignment in assignments:
        start_date = getdate(assignment.start_date)
        end_date = getdate(assignment.end_date)
        
        # Determine new status
        if today_date < start_date:
            new_status = "Planned"
        elif start_date <= today_date <= end_date:
            new_status = "Active"
        else:
            new_status = "Completed"
        
        # Update only if status has changed
        if assignment.status != new_status:
            frappe.db.set_value("Project Assignment", assignment.name, "status", new_status)
            frappe.db.commit()
    
  

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

