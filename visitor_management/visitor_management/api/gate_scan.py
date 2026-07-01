import frappe

@frappe.whitelist()
def scan_pass(pass_code):
    """
    Called by the Security Scanner page when a QR code is scanned.
    Returns visitor details and current status.
    """
    if not pass_code:
        return {"error": "Pass code is required."}
    
    # Look up the Visitor Log by pass_code
    visitor_log = frappe.db.get_value(
        "Visitor Log",
        {"pass_code": pass_code},
        ["name", "visitor_name", "person_to_meet", "purpose_of_visit",
         "valid_from", "valid_till", "status", "check_in_time", "check_out_time",
         "secure_token_url", "number_of_persons", "vehicle_number"],
        as_dict=True
    )
    
    if not visitor_log:
        return {"error": f"No visitor pass found for code: {pass_code}"}
    
    # Check if pass is expired
    from frappe.utils import now_datetime, get_datetime, format_datetime
    now = now_datetime()
    valid_till = get_datetime(visitor_log.valid_till) if visitor_log.valid_till else None
    valid_from = get_datetime(visitor_log.valid_from) if visitor_log.valid_from else None
    
    if valid_from and valid_till and now < valid_from:
        v_from = format_datetime(visitor_log.valid_from, "dd-MM-yyyy hh:mm a")
        v_till = format_datetime(visitor_log.valid_till, "dd-MM-yyyy hh:mm a")
        return {"error": f"This Gatepass is valid from {v_from} to {v_till}. The visitor has arrived too early."}

    is_expired = False
    if valid_till and now > valid_till:
        is_expired = True
    
    # Resolve employee name for person_to_meet
    person_name = None
    if visitor_log.person_to_meet:
        person_name = frappe.db.get_value("Employee", visitor_log.person_to_meet, "employee_name")
    
    return {
        "name": visitor_log.name,
        "visitor_name": visitor_log.visitor_name,
        "person_to_meet": person_name or visitor_log.person_to_meet,
        "purpose_of_visit": visitor_log.purpose_of_visit,
        "number_of_persons": visitor_log.number_of_persons or 1,
        "vehicle_number": visitor_log.vehicle_number or "",
        "valid_till": str(visitor_log.valid_till) if visitor_log.valid_till else None,
        "status": "expired" if is_expired else visitor_log.status,
        "check_in_time": str(visitor_log.check_in_time) if visitor_log.check_in_time else None,
        "check_out_time": str(visitor_log.check_out_time) if visitor_log.check_out_time else None,
        "secure_token_url": visitor_log.secure_token_url
    }


@frappe.whitelist()
def do_checkin(pass_code, vehicle_number=None, vehicle_photo=None):
    """Mark visitor as Checked In with timestamp and vehicle details."""
    from frappe.utils import now_datetime
    
    visitor_log_name = frappe.db.get_value("Visitor Log", {"pass_code": pass_code}, "name")
    if not visitor_log_name:
        return {"error": f"Pass not found: {pass_code}"}
    
    doc = frappe.get_doc("Visitor Log", visitor_log_name)
    
    if doc.status == "Checked In":
        return {"error": f"{doc.visitor_name} is already Checked In!"}
    
    if doc.status == "Checked Out":
        return {"error": f"{doc.visitor_name} has already Checked Out!"}
        
    if not vehicle_number and not vehicle_photo:
        return {"error": "Vehicle Number or Vehicle Photo is required for Check-In."}
    
    doc.status = "Checked In"
    doc.check_in_time = now_datetime()
    if vehicle_number:
        doc.vehicle_number = vehicle_number
    if vehicle_photo:
        doc.vehicle_photo = vehicle_photo
        
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    
    return {
        "success": True,
        "message": f"{doc.visitor_name} has been successfully Checked In!",
        "check_in_time": str(doc.check_in_time)
    }


@frappe.whitelist()
def do_checkout(pass_code):
    """Mark visitor as Checked Out with timestamp."""
    from frappe.utils import now_datetime
    
    visitor_log_name = frappe.db.get_value("Visitor Log", {"pass_code": pass_code}, "name")
    if not visitor_log_name:
        return {"error": f"Pass not found: {pass_code}"}
    
    doc = frappe.get_doc("Visitor Log", visitor_log_name)
    
    if doc.status == "Expected":
        return {"error": f"{doc.visitor_name} has not Checked In yet!"}
    
    if doc.status == "Checked Out":
        return {"error": f"{doc.visitor_name} has already Checked Out!"}
    
    doc.status = "Checked Out"
    doc.check_out_time = now_datetime()
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    
    return {
        "success": True,
        "message": f"{doc.visitor_name} has been successfully Checked Out!",
        "check_out_time": str(doc.check_out_time)
    }
