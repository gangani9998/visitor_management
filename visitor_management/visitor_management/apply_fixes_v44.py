import frappe

def sync_print_format():
    print_doc = frappe.get_doc("Print Format", "Visitor Gate Pass")
    old_html = print_doc.html
    
    # 1. Update QR Code size from 180px to 250px
    new_html = old_html.replace("max-width: 180px;", "max-width: 250px;")
    
    # 2. Append Ji to name
    new_html = new_html.replace("{{ doc.visitor_name }}</td>", "{{ doc.visitor_name }} Ji</td>")
    
    # 3. Change Pass Code label
    new_html = new_html.replace("Pass Code</p>", "Visitor Passcode</p>")
    
    # 4. Use ordinal date formatting in Print Format jinja context
    # In the Print Format, dates are formatted at the top. Let's replace the datetime block.
    old_date_logic = """
    if context.doc.valid_from:
        from frappe.utils import format_datetime
        context.valid_from_formatted = format_datetime(context.doc.valid_from, "dd-MM-yyyy hh:mm a") + " (IST)"
    else:
        context.valid_from_formatted = "Today"
        
    if context.doc.valid_till:
        from frappe.utils import format_datetime
        context.valid_till_formatted = format_datetime(context.doc.valid_till, "dd-MM-yyyy hh:mm a") + " (IST)"
    else:
        context.valid_till_formatted = "N/A"
"""
    new_date_logic = """
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
"""
    new_html = new_html.replace(old_date_logic, new_date_logic)
    
    print_doc.html = new_html
    print_doc.save(ignore_permissions=True)
    frappe.clear_cache()
    print("Print Format synced with Web View successfully!")

if __name__ == "__main__":
    sync_print_format()
