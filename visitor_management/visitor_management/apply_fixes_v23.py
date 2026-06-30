import frappe

def fix_message_anchor():
    # The draft_share_message field was accidentally anchored to 'gate_pass_qr_code'
    # which does not exist (the real field is 'qr_code'). This caused the whole chain
    # to break and float to the top!
    
    frappe.db.set_value("Custom Field", "Visitor Log-draft_share_message", "insert_after", "qr_code")
    frappe.clear_cache()
    print("Fixed Draft Share Message anchor!")

if __name__ == "__main__":
    fix_message_anchor()
