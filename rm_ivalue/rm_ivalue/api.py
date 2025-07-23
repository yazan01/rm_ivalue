# Copyright (c) 2023, Yazan Hamdan and contributors
# For license information, please see license.txt

import frappe
from rm_ivalue.rm_ivalue.tasks import update_project_assignment_status

@frappe.whitelist()
def manual_update_project_status():
    """API endpoint to manually trigger project assignment status update"""
    if not frappe.has_permission("Project Assignment", "write"):
        frappe.throw("Not enough permissions to update Project Assignment status")
    
    try:
        result = update_project_assignment_status()
        frappe.msgprint(result, title="Status Update Complete")
        return {"success": True, "message": result}
    except Exception as e:
        frappe.throw(f"Error updating project status: {str(e)}")

@frappe.whitelist()
def get_project_assignment_summary():
    """Get summary of project assignments by status"""
    if not frappe.has_permission("Project Assignment", "read"):
        frappe.throw("Not enough permissions to read Project Assignment")
    
    try:
        summary = frappe.db.sql("""
            SELECT 
                status,
                COUNT(*) as count,
                COUNT(CASE WHEN docstatus = 1 THEN 1 END) as submitted_count
            FROM `tabProject Assignment`
            WHERE docstatus != 2
            GROUP BY status
            ORDER BY 
                CASE status 
                    WHEN 'Planned' THEN 1 
                    WHEN 'Active' THEN 2 
                    WHEN 'Completed' THEN 3 
                END
        """, as_dict=True)
        
        return summary
    except Exception as e:
        frappe.throw(f"Error getting project assignment summary: {str(e)}")

@frappe.whitelist()
def get_employee_active_assignments(employee=None):
    """Get active assignments for an employee"""
    if not frappe.has_permission("Project Assignment", "read"):
        frappe.throw("Not enough permissions to read Project Assignment")
    
    filters = {
        "status": "Active",
        "docstatus": 1
    }
    
    if employee:
        filters["employee"] = employee
    
    try:
        assignments = frappe.get_all(
            "Project Assignment",
            filters=filters,
            fields=[
                "name", "project", "project_name", "employee", 
                "employee_name", "start_date", "end_date", 
                "allocation_percentage", "status"
            ],
            order_by="start_date asc"
        )
        
        return assignments
    except Exception as e:
        frappe.throw(f"Error getting active assignments: {str(e)}")