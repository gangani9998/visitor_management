import frappe

def remove_duplicate_alert():
    # frappe.utils.copy_to_clipboard natively shows a "Copied to clipboard." alert.
    # We need to remove our custom frappe.show_alert to prevent the double popup!
    
    script_doc = frappe.get_doc("Client Script", "Visitor Log WhatsApp Share")
    old_script = script_doc.script
    
    # Remove the custom alert line
    new_script = old_script.replace("frappe.show_alert({message: __('Message copied to clipboard!'), indicator: 'green'});", "")
    
    script_doc.script = new_script
    script_doc.save(ignore_permissions=True)
    frappe.clear_cache()
    print("Duplicate alert successfully removed!")

if __name__ == "__main__":
    remove_duplicate_alert()
