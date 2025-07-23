// Copyright (c) 2023, Yazan Hamdan and contributors
// For license information, please see license.txt

frappe.ui.form.on('Project Assignment', {
    refresh: function(frm) {
        // Add custom buttons
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Update Status'), function() {
                frappe.call({
                    method: 'rm_ivalue.rm_ivalue.api.manual_update_project_status',
                    callback: function(r) {
                        if (r.message && r.message.success) {
                            frm.reload_doc();
                        }
                    }
                });
            }, __('Actions'));
        }
        
        // Show assignment summary
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Assignment Summary'), function() {
                show_assignment_summary();
            }, __('Reports'));
        }
        
        // Add progress indicators
        if (frm.doc.start_date && frm.doc.end_date) {
            add_progress_indicators(frm);
        }
    },
    
    start_date: function(frm) {
        update_duration_info(frm);
    },
    
    end_date: function(frm) {
        update_duration_info(frm);
    },
    
    employee: function(frm) {
        if (frm.doc.employee) {
            check_employee_workload(frm);
        }
    }
});

function update_duration_info(frm) {
    if (frm.doc.start_date && frm.doc.end_date) {
        let start_date = frappe.datetime.str_to_obj(frm.doc.start_date);
        let end_date = frappe.datetime.str_to_obj(frm.doc.end_date);
        let duration = frappe.datetime.get_diff(end_date, start_date) + 1;
        
        frm.set_intro(__(`Assignment Duration: ${duration} days`), 'blue');
    }
}

function add_progress_indicators(frm) {
    if (frm.doc.docstatus === 1 && frm.doc.status === 'Active') {
        frappe.call({
            method: 'frappe.client.get',
            args: {
                doctype: 'Project Assignment',
                name: frm.doc.name
            },
            callback: function(r) {
                if (r.message) {
                    let today = frappe.datetime.get_today();
                    let start_date = r.message.start_date;
                    let end_date = r.message.end_date;
                    
                    let total_days = frappe.datetime.get_diff(end_date, start_date) + 1;
                    let elapsed_days = Math.max(0, frappe.datetime.get_diff(today, start_date) + 1);
                    let progress = Math.min(100, (elapsed_days / total_days) * 100);
                    
                    let remaining_days = Math.max(0, frappe.datetime.get_diff(end_date, today));
                    
                    frm.dashboard.add_progress(__('Time Progress'), progress, __(`${remaining_days} days remaining`));
                }
            }
        });
    }
}

function check_employee_workload(frm) {
    if (frm.doc.employee && frm.doc.start_date && frm.doc.end_date) {
        frappe.call({
            method: 'rm_ivalue.rm_ivalue.api.get_employee_active_assignments',
            args: {
                employee: frm.doc.employee
            },
            callback: function(r) {
                if (r.message && r.message.length > 0) {
                    let total_allocation = 0;
                    r.message.forEach(function(assignment) {
                        if (assignment.name !== frm.doc.name) {
                            total_allocation += assignment.allocation_percentage;
                        }
                    });
                    
                    let current_allocation = frm.doc.allocation_percentage || 0;
                    let projected_total = total_allocation + current_allocation;
                    
                    if (projected_total > 100) {
                        frm.set_intro(__(`Warning: Employee will be ${projected_total}% allocated (over-allocated)`), 'red');
                    } else if (projected_total > 80) {
                        frm.set_intro(__(`Employee will be ${projected_total}% allocated`), 'orange');
                    }
                }
            }
        });
    }
}

function show_assignment_summary() {
    frappe.call({
        method: 'rm_ivalue.rm_ivalue.api.get_project_assignment_summary',
        callback: function(r) {
            if (r.message) {
                let summary_html = '<table class="table table-bordered"><thead><tr><th>Status</th><th>Total</th><th>Submitted</th></tr></thead><tbody>';
                
                r.message.forEach(function(row) {
                    summary_html += `<tr><td>${row.status}</td><td>${row.count}</td><td>${row.submitted_count}</td></tr>`;
                });
                
                summary_html += '</tbody></table>';
                
                frappe.msgprint({
                    title: __('Project Assignment Summary'),
                    message: summary_html,
                    wide: true
                });
            }
        }
    });
}