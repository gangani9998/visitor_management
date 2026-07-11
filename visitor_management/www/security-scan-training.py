import frappe

def get_context(context):
    # Require login for Security Guard access
    if frappe.session.user == "Guest":
        frappe.throw("Please log in to access the Security Scanner.", frappe.PermissionError)
    context.no_cache = 1
    return context
