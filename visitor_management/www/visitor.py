import frappe

def get_context(context):
    context.no_cache = 1
    token = frappe.form_dict.get("token")
    
    if not token:
        context.error_msg = "No Security Token provided in the URL."
        return context
        
    logs = frappe.get_all("Visitor Log", filters={"secure_token_url": token}, limit=1)
    if not logs:
        context.error_msg = "Gate Pass not found, or the URL has expired."
        return context
        
    context.doc = frappe.get_doc("Visitor Log", logs[0].name)
    
    # 1. Expire link if Checked Out or Expired
    if context.doc.status == "Checked Out":
        context.error_msg = "This Secure Pass has expired because the visitor has already Checked Out."
        return context
        
    if context.doc.status == "expired":
        context.error_msg = "This Secure Pass has expired because the validity period has ended."
        return context
    
    # 2. Fetch real employee name
    if context.doc.person_to_meet:
        emp_name = frappe.db.get_value("Employee", context.doc.person_to_meet, "employee_name")
        context.person_to_meet_name = emp_name or context.doc.person_to_meet
    else:
        context.person_to_meet_name = "N/A"
        
    # 3. Handle 'Other' Purpose
    context.final_purpose = context.doc.specify_purpose if context.doc.purpose_of_visit == "Other" else context.doc.purpose_of_visit
    
    # 4. Fetch Company and Logo
    default_company = frappe.db.get_single_value("Global Defaults", "default_company")
    if default_company:
        company_doc = frappe.get_doc("Company", default_company)
        context.company_name = company_doc.company_name
        context.company_logo = company_doc.company_logo
    else:
        context.company_name = "Company"
        context.company_logo = None
        
    def format_ordinal_date(dt_str):
        if not dt_str: return "Today"
        from frappe.utils import get_datetime
        dt = get_datetime(dt_str)
        day = dt.day
        ordinal = 'th' if 11 <= day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
        return f"{day}{ordinal} of {dt.strftime('%B %Y')}"

    if context.doc.valid_from:
        context.valid_from_formatted = format_ordinal_date(context.doc.valid_from)
    else:
        context.valid_from_formatted = "Today"
        
    if context.doc.valid_till:
        context.valid_till_formatted = format_ordinal_date(context.doc.valid_till)
    else:
        context.valid_till_formatted = "Today"
        
    context.title = f"Gate Pass - {context.doc.visitor_name}"
    return context
