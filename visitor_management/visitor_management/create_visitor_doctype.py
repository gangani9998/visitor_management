import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def create_visitor_log():
    if not frappe.db.exists("DocType", "Visitor Log"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "Visitor Log",
            "module": "Visitor Management",
            "custom": 1,
            "autoname": "format:VIS-.YYYY.-.#####",
            "naming_rule": "Expression",
            "is_submittable": 0,
            "track_changes": 1,
            "fields": [
                {"fieldname": "sb_details", "fieldtype": "Section Break", "label": "Visitor Details"},
                {"fieldname": "visitor_name", "fieldtype": "Data", "label": "Visitor / Contractor Name", "reqd": 1, "in_list_view": 1},
                {"fieldname": "phone", "fieldtype": "Data", "label": "Phone Number", "options": "Phone"},
                {"fieldname": "person_to_meet", "fieldtype": "Link", "label": "Person to Meet", "options": "Employee", "reqd": 1, "in_list_view": 1},
                {"fieldname": "number_of_persons", "fieldtype": "Int", "label": "Number of Persons", "default": "1"},
                
                {"fieldname": "cb_details", "fieldtype": "Column Break"},
                {"fieldname": "visitor_type", "fieldtype": "Select", "label": "Visitor Type", "reqd": 1, "options": "Visitor\nContractor\nVendor\nClient\nInterviewee\nWalk-in\nDelivery Truck"},
                {"fieldname": "purpose_of_visit", "fieldtype": "Select", "label": "Purpose of Visit", "reqd": 1, "options": "Meeting\nMaterial Inward\nMaterial Outward\nMaintenance\nOther"},
                {"fieldname": "specify_purpose", "fieldtype": "Data", "label": "Specify Purpose", "depends_on": "eval:doc.purpose_of_visit=='Other'"},
                {"fieldname": "vehicle_number", "fieldtype": "Data", "label": "Vehicle Number"},
                {"fieldname": "vehicle_photo", "fieldtype": "Attach Image", "label": "Vehicle / Material Photo"},
                
                {"fieldname": "sb_access", "fieldtype": "Section Break", "label": "Access & Validity Logic"},
                {"fieldname": "entry_type", "fieldtype": "Select", "label": "Entry Type", "options": "Single Entry\nMultiple Entry", "default": "Single Entry", "reqd": 1},
                {"fieldname": "valid_from", "fieldtype": "Datetime", "label": "Valid From"},
                {"fieldname": "valid_till", "fieldtype": "Datetime", "label": "Valid Till", "in_list_view": 1},
                
                {"fieldname": "cb_status", "fieldtype": "Column Break"},
                {"fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Expected\nChecked In\nChecked Out\nExpired", "default": "Expected", "reqd": 1, "in_list_view": 1},
                {"fieldname": "check_in_time", "fieldtype": "Datetime", "label": "Check-In Time", "read_only": 1},
                {"fieldname": "check_out_time", "fieldtype": "Datetime", "label": "Check-Out Time", "read_only": 1},
                
                {"fieldname": "sb_security", "fieldtype": "Section Break", "label": "Security Passes (Auto-Generated)"},
                {"fieldname": "pass_code", "fieldtype": "Data", "label": "6-Digit Pass Code", "read_only": 1, "bold": 1},
                {"fieldname": "secure_token_url", "fieldtype": "Data", "label": "Secure Token URL", "hidden": 1},
                
                {"fieldname": "cb_security", "fieldtype": "Column Break"},
                {"fieldname": "qr_code", "fieldtype": "Attach Image", "label": "Gate Pass QR Code", "read_only": 1},
                
                {"fieldname": "sb_share", "fieldtype": "Section Break", "label": "Share Message"},
                {"fieldname": "draft_share_message", "fieldtype": "Text", "label": "Draft Share Message", "read_only": 1}
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
                {"role": "All", "read": 1, "write": 1, "create": 1}
            ]
        })
        doc.insert(ignore_permissions=True)
        print("Successfully created Visitor Log DocType.")
    else:
        print("Visitor Log DocType already exists.")

    frappe.db.commit()

if __name__ == "__main__":
    create_visitor_log()
