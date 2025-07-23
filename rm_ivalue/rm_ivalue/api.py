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

@frappe.whitelist()
def create_end_date_change_request(assignment_name, new_end_date, reason=""):
    """Create change request for end date modification"""
    if not frappe.has_permission("Project Assignment", "write"):
        frappe.throw("Not enough permissions to modify Project Assignment")
    
    try:
        assignment = frappe.get_doc("Project Assignment", assignment_name)
        result = assignment.create_change_request_for_end_date(new_end_date, reason)
        
        return {
            "success": True,
            "message": f"End date change request processed successfully",
            "assignment_name": assignment_name
        }
    except Exception as e:
        frappe.throw(f"Error processing end date change request: {str(e)}")

@frappe.whitelist()
def create_allocation_change_request(assignment_name, new_allocation_percentage, effective_date, reason=""):
    """Create change request for allocation percentage modification"""
    if not frappe.has_permission("Project Assignment", "write"):
        frappe.throw("Not enough permissions to modify Project Assignment")
    
    try:
        assignment = frappe.get_doc("Project Assignment", assignment_name)
        new_assignment_name = assignment.create_change_request_for_allocation(
            float(new_allocation_percentage), effective_date, reason
        )
        
        return {
            "success": True,
            "message": f"Allocation change request processed successfully",
            "original_assignment": assignment_name,
            "new_assignment": new_assignment_name
        }
    except Exception as e:
        frappe.throw(f"Error processing allocation change request: {str(e)}")

@frappe.whitelist()
def get_assignment_change_history(assignment_name):
    """Get change history for an assignment"""
    if not frappe.has_permission("Project Assignment", "read"):
        frappe.throw("Not enough permissions to read Project Assignment")
    
    try:
        # Get comments for this assignment
        comments = frappe.get_all(
            "Comment",
            filters={
                "reference_doctype": "Project Assignment",
                "reference_name": assignment_name,
                "comment_type": "Info"
            },
            fields=["content", "creation", "owner"],
            order_by="creation desc"
        )
        
        # Get related assignments (created from this assignment or vice versa)
        related_assignments = frappe.db.sql("""
            SELECT name, allocation_reference, start_date, end_date, allocation_percentage, status
            FROM `tabProject Assignment`
            WHERE (allocation_reference LIKE %s OR name = %s)
            AND docstatus != 2
            ORDER BY start_date
        """, (f"%{assignment_name}%", assignment_name), as_dict=True)
        
        return {
            "comments": comments,
            "related_assignments": related_assignments
        }
    except Exception as e:
        frappe.throw(f"Error getting assignment change history: {str(e)}")
