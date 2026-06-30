import frappe

@frappe.whitelist()
def get_dashboard_data():
    """API endpoint for the Security Dashboard - returns today's visitor stats."""
    from frappe.utils import today, get_datetime, format_date
    
    today_date = today()
    
    all_today = frappe.get_all("Visitor Log", filters={
        "valid_from": ["<=", today_date + " 23:59:59"],
        "valid_till": [">=", today_date + " 00:00:00"]
    }, fields=["name", "visitor_name", "person_to_meet", "purpose_of_visit",
               "status", "check_in_time", "check_out_time", "valid_till", "pass_code"])
    
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
        v["host"]          = resolve_name(v.person_to_meet)
        v["check_in_fmt"]  = fmt_dt(v.check_in_time)
        v["check_out_fmt"] = fmt_dt(v.check_out_time)
        v["valid_till_fmt"]= fmt_dt(v.valid_till)
        # Convert datetime objects to strings for JSON
        for key in ["check_in_time", "check_out_time", "valid_till"]:
            if v.get(key): v[key] = str(v[key])

    expected    = [v for v in all_today if v.status == "Expected"]
    checked_in  = [v for v in all_today if v.status == "Checked In"]
    checked_out = [v for v in all_today if v.status == "Checked Out"]
    
    today_label = format_date(today_date, "dd MMMM yyyy")

    return {
        "today_date":        today_label,
        "total_today":       len(all_today),
        "total_expected":    len(expected),
        "total_checked_in":  len(checked_in),
        "total_checked_out": len(checked_out),
        "expected":          expected,
        "checked_in":        checked_in,
        "checked_out":       checked_out,
    }
