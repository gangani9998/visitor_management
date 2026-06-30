import frappe

def remove_quick_actions_section():
    # Delete the 'Quick Actions' section break so the buttons naturally 
    # fall into the 'Security Passes (Auto-Generated)' section!
    if frappe.db.exists("Custom Field", "Visitor Log-actions_section"):
        frappe.delete_doc("Custom Field", "Visitor Log-actions_section", ignore_permissions=True)
        
    frappe.clear_cache()
    print("Removed Quick Actions section break successfully!")

if __name__ == "__main__":
    remove_quick_actions_section()
