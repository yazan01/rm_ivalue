# Copyright (c) 2023, Yazan Hamdan and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate, today, date_diff, flt
from frappe.utils.dashboard import cache_source

@frappe.whitelist()
def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)
    summary = get_report_summary(data)
    
    return columns, data, None, chart, summary

def get_columns():
    return [
        {
            "fieldname": "employee",
            "label": "Employee ID",
            "fieldtype": "Link",
            "options": "Employee",
            "width": 120
        },
        {
            "fieldname": "employee_name",
            "label": "Employee Name",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "fieldname": "department",
            "label": "Department",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "designation",
            "label": "Designation",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "status",
            "label": "Employment Status",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "total_assignments",
            "label": "Total Assignments",
            "fieldtype": "Int",
            "width": 120
        },
        {
            "fieldname": "active_assignments",
            "label": "Active Assignments",
            "fieldtype": "Int",
            "width": 120
        },
        {
            "fieldname": "current_allocation",
            "label": "Current Allocation %",
            "fieldtype": "Percent",
            "width": 140
        },
        {
            "fieldname": "allocation_status",
            "label": "Allocation Status",
            "fieldtype": "Data",
            "width": 140
        },
        {
            "fieldname": "upcoming_assignments",
            "label": "Planned Assignments",
            "fieldtype": "Int",
            "width": 130
        },
        {
            "fieldname": "completed_assignments",
            "label": "Completed Assignments",
            "fieldtype": "Int",
            "width": 150
        },
        {
            "fieldname": "last_assignment_end",
            "label": "Last Assignment End",
            "fieldtype": "Date",
            "width": 140
        },
        {
            "fieldname": "availability_date",
            "label": "Next Available Date",
            "fieldtype": "Date",
            "width": 140
        }
    ]

def get_data(filters):
    # Get all employees
    employee_query = """
        SELECT 
            emp.name as employee,
            emp.employee_name,
            emp.department,
            emp.designation,
            emp.status,
            emp.date_of_joining,
            emp.relieving_date
        FROM `tabEmployee` emp
        WHERE emp.status != 'Left'
        ORDER BY emp.employee_name
    """
    
    employees = frappe.db.sql(employee_query, as_dict=True)
    
    # Get all project assignments
    assignment_query = """
        SELECT 
            pa.employee,
            pa.name as assignment_name,
            pa.project,
            pa.project_name,
            pa.start_date,
            pa.end_date,
            pa.allocation_percentage,
            pa.status as assignment_status,
            pa.docstatus
        FROM `tabProject Assignment` pa
        WHERE pa.docstatus != 2
        ORDER BY pa.employee, pa.start_date
    """
    
    assignments = frappe.db.sql(assignment_query, as_dict=True)
    
    # Group assignments by employee
    employee_assignments = {}
    for assignment in assignments:
        emp_id = assignment.employee
        if emp_id not in employee_assignments:
            employee_assignments[emp_id] = []
        employee_assignments[emp_id].append(assignment)
    
    # Process data for each employee
    data = []
    today_date = getdate(today())
    
    for employee in employees:
        emp_id = employee.employee
        emp_assignments = employee_assignments.get(emp_id, [])
        
        # Calculate assignment statistics
        total_assignments = len([a for a in emp_assignments if a.docstatus == 1])
        active_assignments = len([a for a in emp_assignments 
                                if a.assignment_status == 'Active' and a.docstatus == 1])
        planned_assignments = len([a for a in emp_assignments 
                                 if a.assignment_status == 'Planned' and a.docstatus == 1])
        completed_assignments = len([a for a in emp_assignments 
                                   if a.assignment_status == 'Completed' and a.docstatus == 1])
        
        # Calculate current allocation
        current_allocation = 0
        for assignment in emp_assignments:
            if (assignment.assignment_status == 'Active' and 
                assignment.docstatus == 1 and
                getdate(assignment.start_date) <= today_date <= getdate(assignment.end_date)):
                current_allocation += flt(assignment.allocation_percentage)
        
        # Determine allocation status
        if current_allocation == 0:
            allocation_status = "Available"
        elif current_allocation <= 100:
            allocation_status = "Allocated"
        else:
            allocation_status = "Over-allocated"
        
        # Find last assignment end date
        last_assignment_end = None
        submitted_assignments = [a for a in emp_assignments if a.docstatus == 1]
        if submitted_assignments:
            last_assignment_end = max([getdate(a.end_date) for a in submitted_assignments])
        
        # Calculate availability date
        availability_date = None
        active_and_planned = [a for a in emp_assignments 
                            if a.assignment_status in ['Active', 'Planned'] and a.docstatus == 1]
        if active_and_planned:
            availability_date = max([getdate(a.end_date) for a in active_and_planned])
            if availability_date <= today_date:
                availability_date = today_date
        else:
            availability_date = today_date
        
        data.append({
            "employee": emp_id,
            "employee_name": employee.employee_name,
            "department": employee.department,
            "designation": employee.designation,
            "status": employee.status,
            "total_assignments": total_assignments,
            "active_assignments": active_assignments,
            "current_allocation": current_allocation,
            "allocation_status": allocation_status,
            "upcoming_assignments": planned_assignments,
            "completed_assignments": completed_assignments,
            "last_assignment_end": last_assignment_end,
            "availability_date": availability_date
        })
    
    return data

def get_chart_data(data):
    # Chart 1: Allocation Status Distribution
    allocation_status_count = {}
    department_allocation = {}
    
    for row in data:
        # Count allocation status
        status = row.get('allocation_status', 'Available')
        allocation_status_count[status] = allocation_status_count.get(status, 0) + 1
        
        # Department wise allocation
        dept = row.get('department', 'No Department')
        if dept not in department_allocation:
            department_allocation[dept] = {'total': 0, 'allocated': 0}
        department_allocation[dept]['total'] += 1
        if row.get('current_allocation', 0) > 0:
            department_allocation[dept]['allocated'] += 1
    
    charts = [
        {
            "name": "Allocation Status Distribution",
            "chart_name": "Allocation Status",
            "chart_type": "donut",
            "data": {
                "labels": list(allocation_status_count.keys()),
                "datasets": [{
                    "name": "Employees",
                    "values": list(allocation_status_count.values())
                }]
            }
        },
        {
            "name": "Department Allocation Overview",
            "chart_name": "Department Allocation",
            "chart_type": "bar",
            "data": {
                "labels": list(department_allocation.keys()),
                "datasets": [
                    {
                        "name": "Total Employees",
                        "values": [dept_data['total'] for dept_data in department_allocation.values()]
                    },
                    {
                        "name": "Allocated Employees",
                        "values": [dept_data['allocated'] for dept_data in department_allocation.values()]
                    }
                ]
            }
        }
    ]
    
    return charts

def get_report_summary(data):
    total_employees = len(data)
    available_employees = len([d for d in data if d.get('allocation_status') == 'Available'])
    allocated_employees = len([d for d in data if d.get('allocation_status') == 'Allocated'])
    over_allocated_employees = len([d for d in data if d.get('allocation_status') == 'Over-allocated'])
    
    total_active_assignments = sum([d.get('active_assignments', 0) for d in data])
    avg_allocation = sum([d.get('current_allocation', 0) for d in data]) / total_employees if total_employees > 0 else 0
    
    return [
        {
            "value": total_employees,
            "label": "Total Employees",
            "indicator": "Blue",
            "datatype": "Int"
        },
        {
            "value": available_employees,
            "label": "Available Employees",
            "indicator": "Green",
            "datatype": "Int"
        },
        {
            "value": allocated_employees,
            "label": "Allocated Employees",
            "indicator": "Orange",
            "datatype": "Int"
        },
        {
            "value": over_allocated_employees,
            "label": "Over-allocated Employees",
            "indicator": "Red",
            "datatype": "Int"
        },
        {
            "value": total_active_assignments,
            "label": "Total Active Assignments",
            "indicator": "Blue",
            "datatype": "Int"
        },
        {
            "value": round(avg_allocation, 1),
            "label": "Average Allocation %",
            "indicator": "Purple",
            "datatype": "Percent"
        }
    ]

@frappe.whitelist()
def get_employee_assignment_details(employee):
    """Get detailed assignment information for a specific employee"""
    if not frappe.has_permission("Project Assignment", "read"):
        frappe.throw("Not enough permissions to read Project Assignment")
    
    assignments = frappe.get_all(
        "Project Assignment",
        filters={
            "employee": employee,
            "docstatus": ["!=", 2]
        },
        fields=[
            "name", "project", "project_name", "start_date", "end_date",
            "allocation_percentage", "status", "docstatus", "creation"
        ],
        order_by="start_date desc"
    )
    
    return assignments

@frappe.whitelist()
def get_department_summary():
    """Get department-wise summary"""
    if not frappe.has_permission("Employee", "read"):
        frappe.throw("Not enough permissions to read Employee")
    
    query = """
        SELECT 
            COALESCE(emp.department, 'No Department') as department,
            COUNT(emp.name) as total_employees,
            COUNT(CASE WHEN emp.status = 'Active' THEN 1 END) as active_employees,
            COUNT(DISTINCT pa.employee) as employees_with_assignments,
            COUNT(CASE WHEN pa.status = 'Active' AND pa.docstatus = 1 THEN 1 END) as active_assignments,
            ROUND(AVG(CASE WHEN pa.status = 'Active' AND pa.docstatus = 1 THEN pa.allocation_percentage END), 2) as avg_allocation
        FROM `tabEmployee` emp
        LEFT JOIN `tabProject Assignment` pa ON emp.name = pa.employee AND pa.docstatus = 1
        WHERE emp.status != 'Left'
        GROUP BY COALESCE(emp.department, 'No Department')
        ORDER BY total_employees DESC
    """
    
    return frappe.db.sql(query, as_dict=True)