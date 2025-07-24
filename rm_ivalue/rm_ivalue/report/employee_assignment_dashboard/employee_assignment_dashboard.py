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
        {"fieldname": "employee", "label": "Employee ID", "fieldtype": "Link", "options": "Employee", "width": 120},
        {"fieldname": "employee_name", "label": "Employee Name", "fieldtype": "Data", "width": 200},
        {"fieldname": "department", "label": "Department", "fieldtype": "Data", "width": 150},
        {"fieldname": "designation", "label": "Designation", "fieldtype": "Data", "width": 150},
        {"fieldname": "status", "label": "Employment Status", "fieldtype": "Data", "width": 120},
        {"fieldname": "total_assignments", "label": "Total Assignments", "fieldtype": "Int", "width": 120},
        {"fieldname": "active_assignments", "label": "Active Assignments", "fieldtype": "Int", "width": 120},
        {"fieldname": "current_allocation", "label": "Current Allocation %", "fieldtype": "Percent", "width": 140},
        {"fieldname": "allocation_status", "label": "Allocation Status", "fieldtype": "Data", "width": 140},
        {"fieldname": "upcoming_assignments", "label": "Planned Assignments", "fieldtype": "Int", "width": 130},
        {"fieldname": "completed_assignments", "label": "Completed Assignments", "fieldtype": "Int", "width": 150},
        {"fieldname": "last_assignment_end", "label": "Last Assignment End", "fieldtype": "Date", "width": 140},
        {"fieldname": "availability_date", "label": "Next Available Date", "fieldtype": "Date", "width": 140}
    ]

def get_data(filters):
    from_date = getdate(filters.get("from_date")) if filters and filters.get("from_date") else None
    to_date = getdate(filters.get("to_date")) if filters and filters.get("to_date") else None

    employee_query = """
        SELECT name as employee, employee_name, department, designation, status, date_of_joining, relieving_date
        FROM `tabEmployee` WHERE status != 'Left' ORDER BY employee_name
    """
    employees = frappe.db.sql(employee_query, as_dict=True)

    assignment_query = f"""
        SELECT pa.employee, pa.name as assignment_name, pa.project, pa.project_name,
               pa.start_date, pa.end_date, pa.allocation_percentage, pa.status as assignment_status, pa.docstatus
        FROM `tabProject Assignment` pa
        WHERE pa.docstatus != 2
        {"AND pa.start_date <= '{0}'".format(to_date) if to_date else ""}
        {"AND pa.end_date >= '{0}'".format(from_date) if from_date else ""}
        ORDER BY pa.employee, pa.start_date
    """
    assignments = frappe.db.sql(assignment_query, as_dict=True)

    employee_assignments = {}
    for assignment in assignments:
        emp_id = assignment.employee
        if emp_id not in employee_assignments:
            employee_assignments[emp_id] = []
        employee_assignments[emp_id].append(assignment)

    data = []
    today_date = getdate(today())

    for employee in employees:
        emp_id = employee.employee
        emp_assignments = employee_assignments.get(emp_id, [])
        total_assignments = len([a for a in emp_assignments if a.docstatus == 1])
        active_assignments = len([a for a in emp_assignments if a.assignment_status == 'Active' and a.docstatus == 1])
        planned_assignments = len([a for a in emp_assignments if a.assignment_status == 'Planned' and a.docstatus == 1])
        completed_assignments = len([a for a in emp_assignments if a.assignment_status == 'Completed' and a.docstatus == 1])

        current_allocation = 0
        for assignment in emp_assignments:
            if assignment.assignment_status == 'Active' and assignment.docstatus == 1 and getdate(assignment.start_date) <= today_date <= getdate(assignment.end_date):
                current_allocation += flt(assignment.allocation_percentage)

        allocation_status = "Available"
        if current_allocation > 0 and current_allocation <= 100:
            allocation_status = "Allocated"
        elif current_allocation > 100:
            allocation_status = "Over-allocated"

        last_assignment_end = None
        submitted_assignments = [a for a in emp_assignments if a.docstatus == 1]
        if submitted_assignments:
            last_assignment_end = max([getdate(a.end_date) for a in submitted_assignments])

        availability_date = today_date
        active_and_planned = [a for a in emp_assignments if a.assignment_status in ['Active', 'Planned'] and a.docstatus == 1]
        if active_and_planned:
            availability_date = max([getdate(a.end_date) for a in active_and_planned])
            if availability_date <= today_date:
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

@frappe.whitelist()
def get_timeline_assignments(from_date=None, to_date=None):
    if not from_date or not to_date:
        frappe.throw("Please select both From Date and To Date")

    query = """
        SELECT pa.employee, emp.employee_name, pa.project_name,
               pa.start_date, pa.end_date, pa.allocation_percentage
        FROM `tabProject Assignment` pa
        JOIN `tabEmployee` emp ON pa.employee = emp.name
        WHERE pa.docstatus = 1
        AND pa.start_date <= %(to_date)s
        AND pa.end_date >= %(from_date)s
    """

    return frappe.db.sql(query, {
        "from_date": from_date,
        "to_date": to_date
    }, as_dict=True)
