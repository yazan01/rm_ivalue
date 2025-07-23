# Copyright (c) 2023, Yazan Hamdan and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate, today

def update_project_assignment_status():
    """Daily task to update status of all submitted Project Assignments"""
    try:
        # Get all submitted Project Assignments
        assignments = frappe.get_all(
            "Project Assignment",
            filters={"docstatus": 1},  # Only submitted documents
            fields=["name", "start_date", "end_date", "status"]
        )
        
        today_date = getdate(today())
        updated_count = 0
        
        for assignment in assignments:
            start_date = getdate(assignment.start_date)
            end_date = getdate(assignment.end_date)
            current_status = assignment.status
            
            # Determine new status based on dates
            if today_date < start_date:
                new_status = "Planned"
            elif start_date <= today_date <= end_date:
                new_status = "Active"
            else:  # today_date > end_date
                new_status = "Completed"
            
            # Update only if status has changed
            if current_status != new_status:
                frappe.db.set_value(
                    "Project Assignment", 
                    assignment.name, 
                    "status", 
                    new_status,
                    update_modified=False  # Don't update modified timestamp
                )
                updated_count += 1
        
        # Commit the changes
        frappe.db.commit()
        
        # Log the update
        if updated_count > 0:
            frappe.logger().info(f"Updated status for {updated_count} Project Assignments")
        
        return f"Successfully updated {updated_count} project assignments"
        
    except Exception as e:
        frappe.logger().error(f"Error updating Project Assignment status: {str(e)}")
        frappe.db.rollback()
        raise e

def all():
    """Function that runs on all scheduler events"""
    pass

def daily():
    """Function that runs daily"""
    update_project_assignment_status()

def hourly():
    """Function that runs hourly"""
    pass

def weekly():
    """Function that runs weekly"""
    pass

def monthly():
    """Function that runs monthly"""
    pass