import frappe
import qrcode
import io

def regenerate_qr_codes():
    logs = frappe.get_all("Visitor Log", fields=["name", "pass_code", "qr_code"])
    
    for log in logs:
        if not log.pass_code:
            continue
        
        # Delete the old QR file if it exists
        if log.qr_code:
            old_file = frappe.db.get_value("File", {"file_url": log.qr_code}, "name")
            if old_file:
                frappe.delete_doc("File", old_file, ignore_permissions=True, force=1)
            frappe.db.set_value("Visitor Log", log.name, "qr_code", None, update_modified=False)
        
        # Generate new QR code with border=1 (minimal quiet zone)
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=1)
        qr.add_data(log.pass_code)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        file_content = img_byte_arr.getvalue()
        
        file_name = f"QR_{log.pass_code}.png"
        saved_file = frappe.get_doc({
            "doctype": "File",
            "file_name": file_name,
            "attached_to_doctype": "Visitor Log",
            "attached_to_name": log.name,
            "attached_to_field": "qr_code",
            "is_private": 0,
            "content": file_content
        })
        saved_file.save(ignore_permissions=True)
        frappe.db.set_value("Visitor Log", log.name, "qr_code", saved_file.file_url, update_modified=False)
    
    frappe.db.commit()
    print(f"Successfully regenerated QR codes for {len(logs)} passes with minimal border!")

if __name__ == "__main__":
    regenerate_qr_codes()
