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

            // Add Change Request buttons
            frm.add_custom_button(__('Change End Date'), function() {
                show_end_date_change_dialog(frm);
            }, __('Change Request'));

            frm.add_custom_button(__('Change Allocation %'), function() {
                show_allocation_change_dialog(frm);
            }, __('Change Request'));

            frm.add_custom_button(__('View Change History'), function() {
                show_change_history(frm);
            }, __('Change Request'));
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

function show_end_date_change_dialog(frm) {
    let dialog = new frappe.ui.Dialog({
        title: __('Change End Date'),
        fields: [
            {
                fieldtype: 'Date',
                fieldname: 'new_end_date',
                label: __('New End Date'),
                reqd: 1,
                default: frm.doc.end_date
            },
            {
                fieldtype: 'Small Text',
                fieldname: 'reason',
                label: __('Reason for Change'),
                reqd: 1
            }
        ],
        primary_action: function(values) {
            frappe.call({
                method: 'rm_ivalue.rm_ivalue.api.create_end_date_change_request',
                args: {
                    assignment_name: frm.doc.name,
                    new_end_date: values.new_end_date,
                    reason: values.reason
                },
                callback: function(r) {
                    if (r.message && r.message.success) {
                        frappe.msgprint(__('End date change request processed successfully'));
                        frm.reload_doc();
                        dialog.hide();
                    }
                }
            });
        },
        primary_action_label: __('Submit Change Request')
    });
    
    dialog.show();
}

function show_allocation_change_dialog(frm) {
    let dialog = new frappe.ui.Dialog({
        title: __('Change Allocation Percentage'),
        fields: [
            {
                fieldtype: 'Percent',
                fieldname: 'new_allocation_percentage',
                label: __('New Allocation Percentage'),
                reqd: 1,
                default: frm.doc.allocation_percentage
            },
            {
                fieldtype: 'Date',
                fieldname: 'effective_date',
                label: __('Effective Date'),
                reqd: 1,
                default: frappe.datetime.add_days(frappe.datetime.get_today(), 1)
            },
            {
                fieldtype: 'Small Text',
                fieldname: 'reason',
                label: __('Reason for Change'),
                reqd: 1
            },
            {
                fieldtype: 'HTML',
                fieldname: 'info',
                options: `<div class="alert alert-info">
                    <strong>Note:</strong> This will:
                    <ul>
                        <li>Update current assignment end date to: <span id="new-end-date">${frappe.datetime.add_days(frappe.datetime.get_today(), -1)}</span></li>
                        <li>Create new assignment starting from effective date</li>
                        <li>New assignment will have the same project and employee</li>
                    </ul>
                </div>`
            }
        ],
        primary_action: function(values) {
            frappe.call({
                method: 'rm_ivalue.rm_ivalue.api.create_allocation_change_request',
                args: {
                    assignment_name: frm.doc.name,
                    new_allocation_percentage: values.new_allocation_percentage,
                    effective_date: values.effective_date,
                    reason: values.reason
                },
                callback: function(r) {
                    if (r.message && r.message.success) {
                        frappe.msgprint({
                            title: __('Success'),
                            message: __('Allocation change request processed successfully. New assignment: ') + r.message.new_assignment,
                            indicator: 'green'
                        });
                        frm.reload_doc();
                        dialog.hide();
                    }
                }
            });
        },
        primary_action_label: __('Submit Change Request')
    });
    
    // Update info section when effective date changes
    dialog.fields_dict.effective_date.$input.on('change', function() {
        let effective_date = dialog.get_value('effective_date');
        if (effective_date) {
            let new_end_date = frappe.datetime.add_days(effective_date, -1);
            dialog.fields_dict.info.$wrapper.find('#new-end-date').text(new_end_date);
        }
    });
    
    dialog.show();
}

function show_change_history(frm) {
    frappe.call({
        method: 'rm_ivalue.rm_ivalue.api.get_assignment_change_history',
        args: {
            assignment_name: frm.doc.name
        },
        callback: function(r) {
            if (r.message) {
                let history_html = '<div class="change-history">';
                
                // Show related assignments
                if (r.message.related_assignments && r.message.related_assignments.length > 0) {
                    history_html += '<h5>Related Assignments</h5>';
                    history_html += '<table class="table table-bordered table-sm"><thead><tr><th>Assignment</th><th>Start Date</th><th>End Date</th><th>Allocation %</th><th>Status</th><th>Reference</th></tr></thead><tbody>';
                    
                    r.message.related_assignments.forEach(function(assignment) {
                        let row_class = assignment.name === frm.doc.name ? 'table-primary' : '';
                        history_html += `<tr class="${row_class}">
                            <td><a href="/app/project-assignment/${assignment.name}">${assignment.name}</a></td>
                            <td>${assignment.start_date}</td>
                            <td>${assignment.end_date}</td>
                            <td>${assignment.allocation_percentage}%</td>
                            <td><span class="indicator ${get_status_color(assignment.status)}">${assignment.status}</span></td>
                            <td>${assignment.allocation_reference || ''}</td>
                        </tr>`;
                    });
                    
                    history_html += '</tbody></table>';
                }
                
                // Show comments/changes
                if (r.message.comments && r.message.comments.length > 0) {
                    history_html += '<h5 class="mt-3">Change Log</h5>';
                    r.message.comments.forEach(function(comment) {
                        history_html += `<div class="alert alert-secondary">
                            <small class="text-muted">${frappe.datetime.str_to_user(comment.creation)} by ${comment.owner}</small><br>
                            ${comment.content}
                        </div>`;
                    });
                }
                
                history_html += '</div>';
                
                frappe.msgprint({
                    title: __('Change History for ') + frm.doc.name,
                    message: history_html,
                    wide: true
                });
            }
        }
    });
}

function get_status_color(status) {
    switch(status) {
        case 'Planned': return 'blue';
        case 'Active': return 'green';
        case 'Completed': return 'gray';
        default: return 'gray';
    }
}
