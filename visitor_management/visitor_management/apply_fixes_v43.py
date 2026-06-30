import frappe
from frappe.utils import get_url, get_datetime

def safe_regenerate_link_above():
    company_name = frappe.db.get_single_value("Global Defaults", "default_company") or "Our Company"
    logs = frappe.get_all("Visitor Log", fields=["name", "visitor_name", "pass_code", "secure_token_url", "valid_from"])
    
    for log in logs:
        if log.pass_code and log.secure_token_url:
            if log.valid_from:
                dt = get_datetime(log.valid_from)
                day = dt.day
                ordinal = 'th' if 11 <= day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
                formatted_date = f"{day}{ordinal} of {dt.strftime('%B %Y')}"
            else:
                formatted_date = "Today"

            message = f"Dear {log.visitor_name} Ji,\n\n"
            message += f"Your upcoming visit to {company_name} has been scheduled. We are expecting you on: {formatted_date}\n"
            message += f"Your Gate Pass has been successfully generated for your upcoming visit.\n\n"
            message += f"Visitor Passcode: {log.pass_code}\n\n"
            message += f"{get_url()}/visitor?token={log.secure_token_url}\n\n"
            message += f"Please click the secure link above to open your Digital Gate Pass, which contains your scannable QR Code and present this to the Security Guard upon arrival for quick entry and Exit."
            
            frappe.db.set_value("Visitor Log", log.name, "draft_share_message", message)
            
    frappe.db.commit()
    print("Messages successfully updated with link at the top!")

if __name__ == "__main__":
    safe_regenerate_link_above()
