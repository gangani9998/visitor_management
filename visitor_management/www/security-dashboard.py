import frappe
from frappe.utils import today, now_datetime, get_datetime

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw("Please log in to access the Security Dashboard.", frappe.PermissionError)
    
    context.no_cache = 1
    today_date = today()
    
    # Stats
    all_today = frappe.get_all("Visitor Log", filters={
        "valid_from": ["<=", today_date + " 23:59:59"],
        "valid_till": [">=", today_date + " 00:00:00"]
    }, fields=["name", "visitor_name", "person_to_meet", "department", "purpose_of_visit",
               "status", "check_in_time", "check_out_time", "valid_till", "pass_code"])
    
    expected    = [v for v in all_today if v.status == "Expected"]
    checked_in  = [v for v in all_today if v.status == "Checked In"]
    checked_out = [v for v in all_today if v.status == "Checked Out"]
    
    # Resolve employee names
    def resolve_name(emp_id):
        if not emp_id: return "—"
        return frappe.db.get_value("Employee", emp_id, "employee_name") or emp_id
    
    def fmt_dt(dt_val):
        if not dt_val: return "—"
        try:
            dt = get_datetime(dt_val)
            return dt.strftime("%d %b, %I:%M %p")
        except:
            return str(dt_val)
    
    for v in all_today:
        v["host"] = resolve_name(v.person_to_meet)
        v["check_in_fmt"]  = fmt_dt(v.check_in_time)
        v["check_out_fmt"] = fmt_dt(v.check_out_time)
        v["valid_till_fmt"] = fmt_dt(v.valid_till)

    context.expected    = expected
    context.checked_in  = checked_in
    context.checked_out = checked_out
    context.total_today      = len(all_today)
    context.total_expected   = len(expected)
    context.total_checked_in = len(checked_in)
    context.total_checked_out= len(checked_out)
    context.today_date = frappe.utils.format_date(today_date, "dd MMMM yyyy")
    context.title = "Security Gate Dashboard"
    return context
