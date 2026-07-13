import frappe
from frappe.utils import now_datetime, random_string, get_url
import uuid
import qrcode
import io
import base64

def validate(doc, method):
    # 1. Generate 6-Digit Pass Code on first save
    if not doc.pass_code:
        doc.pass_code = random_string(6).upper()

    # 2. Generate Secure Token URL on first save
    if not doc.secure_token_url:
        doc.secure_token_url = str(uuid.uuid4().hex)

    # 3. Validation Logic
    from frappe.utils import get_datetime
    if doc.valid_from and doc.valid_till:
        valid_from_dt = get_datetime(doc.valid_from)
        valid_till_dt = get_datetime(doc.valid_till)
        if valid_from_dt > valid_till_dt:
            frappe.throw("Error: 'Valid From' time cannot be after 'Valid Till' time.")

    # 4. Status Routing Logic
    if not doc.is_new() and doc.status == "Checked Out":
        if doc.entry_type == "Single Entry":
            pass # Deny re-entry handled at UI level or throw here if they try to change to Checked In?
            # Wait, if they try to check in again:
            old_doc = doc.get_doc_before_save()
            if old_doc and old_doc.status == "Checked Out" and doc.status == "Checked In":
                frappe.throw("Error: Code already used. Single Entry pass is expired.")
        
    # Auto-stamp check-in / check-out times based on status transition
    if not doc.is_new():
        old_doc = doc.get_doc_before_save()
        if old_doc:
            if old_doc.status != "Checked In" and doc.status == "Checked In":
                doc.check_in_time = now_datetime()
            elif old_doc.status != "Checked Out" and doc.status == "Checked Out":
                doc.check_out_time = now_datetime()

    # 6. Auto-generate Draft Share Message
    if doc.pass_code and doc.secure_token_url:
        from frappe.utils import get_datetime, format_datetime
        
        company_name = frappe.db.get_single_value("Global Defaults", "default_company") or "Our Company"
        message = f"Dear {doc.visitor_name} Ji,\n\n"
        
        if doc.valid_from and doc.valid_till:
            dt_from = get_datetime(doc.valid_from)
            dt_till = get_datetime(doc.valid_till)
            
            day = dt_from.day
            ordinal = 'th' if 11 <= day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
            formatted_date = f"{day}{ordinal} of {dt_from.strftime('%B %Y')}"
            
            v_from_str = format_datetime(doc.valid_from, "dd-MM-yyyy hh:mm a")
            v_till_str = format_datetime(doc.valid_till, "dd-MM-yyyy hh:mm a")
            
            if dt_from.date() == dt_till.date():
                v_from_time = format_datetime(doc.valid_from, "hh:mm a")
                v_till_time = format_datetime(doc.valid_till, "hh:mm a")
                message += f"Your upcoming visit to {company_name} has been scheduled for the {formatted_date}.\n"
                message += f"Your Gate Pass has been successfully generated and is valid from {v_from_time} to {v_till_time}.\n\n"
            else:
                message += f"Your upcoming visit to {company_name} has been scheduled.\n"
                message += f"Your Gate Pass has been successfully generated and is valid from {v_from_str} to {v_till_str}.\n\n"
        else:
            message += f"Your upcoming visit to {company_name} has been scheduled.\n"
            message += f"Your Gate Pass has been successfully generated.\n\n"
        v_type = doc.visitor_type if doc.visitor_type else "Visitor"
        message += f"{v_type} Passcode: {doc.pass_code}\n\n"
        message += f"{get_url()}/visitor?token={doc.secure_token_url}\n\n"
        message += f"Please click the secure link above to open your Digital Gate Pass, which contains your scannable QR Code and present this to the Security Guard upon arrival for quick entry and Exit."
        doc.draft_share_message = message

def on_update(doc, method):
    # 5. Generate QR Code Image if not exists
    if doc.pass_code and not doc.qr_code:
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=1)
        qr.add_data(doc.pass_code)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        file_content = img_byte_arr.getvalue()
        
        file_name = f"QR_{doc.pass_code}.png"
        
        # Create File document securely
        saved_file = frappe.get_doc({
            "doctype": "File",
            "file_name": file_name,
            "attached_to_doctype": "Visitor Log",
            "attached_to_name": doc.name,
            "attached_to_field": "qr_code",
            "is_private": 0,
            "content": file_content
        })
        saved_file.insert(ignore_permissions=True)
        
        # We need to set the qr_code field to the file url and save again
        frappe.db.set_value("Visitor Log", doc.name, "qr_code", saved_file.file_url, update_modified=False)
