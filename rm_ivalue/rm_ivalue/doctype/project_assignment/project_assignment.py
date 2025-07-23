# Copyright (c) 2023, Yazan Hamdan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import date_diff, flt, getdate, today, add_days

class ProjectAssignment(Document):
    def validate(self):
        self.validate_dates()
        self.validate_allocation_percentage()
        
    def validate_dates(self):
        # Check if end date is after start date
        if self.end_date and self.start_date and self.end_date < self.start_date:
            frappe.throw("End Date cannot be before Start Date")
    
    def validate_allocation_percentage(self):
        # Ensure allocation percentage is between 0 and 100
        if self.allocation_percentage and (self.allocation_percentage < 0 or self.allocation_percentage > 100):
            frappe.throw("Allocation Percentage must be between 0% and 100%")
    
    def before_save(self):
        """Update status before saving if not submitted"""
        if self.docstatus == 0:  # Draft
            self.update_status_based_on_dates()
    
    def on_submit(self):
        """Update status after submit based on dates"""
        self.update_status_based_on_dates()
    
    def update_status_based_on_dates(self):
        """Update status based on current date and assignment dates"""
        today_date = getdate(today())
        start_date = getdate(self.start_date)
        end_date = getdate(self.end_date)
        
        if today_date < start_date:
            self.status = "Planned"
        elif start_date <= today_date <= end_date:
            self.status = "Active"
        else:
            self.status = "Completed"
    
    def is_active(self):
        """Check if this assignment is currently active"""
        today_date = getdate(today())
        return (getdate(self.start_date) <= today_date <= getdate(self.end_date))
    
    def get_remaining_days(self):
        """Get remaining days in this assignment"""
        today_date = getdate(today())
        if today_date > getdate(self.end_date):
            return 0
        elif today_date < getdate(self.start_date):
            return date_diff(self.end_date, self.start_date) + 1
        else:
            return date_diff(self.end_date, today_date)
    
    def get_total_days(self):
        """Get total days in this assignment"""
        return date_diff(self.end_date, self.start_date) + 1
    
    def get_elapsed_days(self):
        """Get elapsed days since assignment started"""
        today_date = getdate(today())
        start_date = getdate(self.start_date)
        
        if today_date < start_date:
            return 0
        elif today_date > getdate(self.end_date):
            return self.get_total_days()
        else:
            return date_diff(today_date, self.start_date) + 1
    
    def get_progress_percentage(self):
        """Get progress percentage based on elapsed time"""
        total_days = self.get_total_days()
        elapsed_days = self.get_elapsed_days()
        
        if total_days <= 0:
            return 0
        
        progress = (elapsed_days / total_days) * 100
        return min(100, max(0, progress))

    def create_change_request_for_end_date(self, new_end_date, reason=""):
        """Create change request for end date modification"""
        if self.docstatus != 1:
            frappe.throw("Can only create change requests for submitted assignments")
        
        # Validate new end date
        if getdate(new_end_date) <= getdate(self.start_date):
            frappe.throw("New end date must be after start date")
        
        # Update current document's end date
        frappe.db.set_value("Project Assignment", self.name, "end_date", new_end_date)
        frappe.db.set_value("Project Assignment", self.name, "allocation_reference", 
                           f"End date changed from {self.end_date} to {new_end_date}. Reason: {reason}")
        
        # Log the change
        self.add_comment("Info", f"End date changed from {self.end_date} to {new_end_date}. Reason: {reason}")
        
        frappe.msgprint(f"End date successfully updated to {new_end_date}")
        return True

    def create_change_request_for_allocation(self, new_allocation_percentage, effective_date, reason=""):
        """Create change request for allocation percentage modification"""
        if self.docstatus != 1:
            frappe.throw("Can only create change requests for submitted assignments")
        
        # Validate effective date
        effective_date = getdate(effective_date)
        if effective_date <= getdate(self.start_date):
            frappe.throw("Effective date must be after current start date")
        
        if effective_date > getdate(self.end_date):
            frappe.throw("Effective date cannot be after end date")
        
        # Validate allocation percentage
        if new_allocation_percentage < 0 or new_allocation_percentage > 100:
            frappe.throw("Allocation percentage must be between 0% and 100%")
        
        # Store original end date
        original_end_date = self.end_date
        
        # Update current document - set end date to effective_date - 1
        new_end_date_for_current = add_days(effective_date, -1)
        frappe.db.set_value("Project Assignment", self.name, "end_date", new_end_date_for_current)
        frappe.db.set_value("Project Assignment", self.name, "allocation_reference", 
                           f"Allocation changed from {self.allocation_percentage}% to {new_allocation_percentage}% effective {effective_date}. Reason: {reason}")
        
        # Create new assignment with new allocation
        new_assignment = frappe.get_doc({
            "doctype": "Project Assignment",
            "project": self.project,
            "project_name": self.project_name,
            "employee": self.employee,
            "employee_name": self.employee_name,
            "start_date": effective_date,
            "end_date": original_end_date,
            "allocation_percentage": new_allocation_percentage,
            "status": "Planned",  # Will be updated based on dates
            "allocation_reference": f"Created from CR of {self.name}. New allocation: {new_allocation_percentage}%. Reason: {reason}"
        })
        
        new_assignment.insert()
        new_assignment.submit()
        
        # Add comments to both documents
        self.add_comment("Info", f"Allocation changed from {self.allocation_percentage}% to {new_allocation_percentage}% effective {effective_date}. New assignment created: {new_assignment.name}")
        new_assignment.add_comment("Info", f"Created from change request of {self.name}")
        
        frappe.msgprint(f"Allocation change processed successfully. New assignment created: {new_assignment.name}")
        return new_assignment.name

# Utility functions for API calls
def get_employee_workload(employee, start_date=None, end_date=None):
    """Calculate total workload for an employee in a given period"""
    filters = {
        "employee": employee,
        "docstatus": 1,
        "status": ["in", ["Planned", "Active"]]
    }
    
    if start_date:
        filters["start_date"] = [">=", start_date]
    if end_date:
        filters["end_date"] = ["<=", end_date]
    
    assignments = frappe.get_all(
        "Project Assignment",
        filters=filters,
        fields=["allocation_percentage", "start_date", "end_date"]
    )
    
    # Calculate overlapping periods and total allocation
    # This is a simplified calculation - for more complex scenarios,
    # you might need to handle overlapping date ranges more precisely
    total_allocation = sum([assignment.allocation_percentage for assignment in assignments])
    
    return {
        "total_assignments": len(assignments),
        "total_allocation": total_allocation,
        "is_overallocated": total_allocation > 100
    }
