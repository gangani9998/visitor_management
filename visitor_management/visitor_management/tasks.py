import frappe
from frappe.utils import now_datetime

def expire_visitor_passes():
    """
    Scheduled task to mark Visitor Log entries as 'Expired' 
    if their valid_till datetime has passed and they are still 'Expected'.
    """
    frappe.db.sql("""
        UPDATE `tabVisitor Log` 
        SET status = 'Expired' 
        WHERE status = 'Expected' 
        AND valid_till < %s
    """, (now_datetime(),))
    
    # Auto-checkout anyone who was left "Checked In" after their pass expired
    # We set their checkout time to exactly when their pass was supposed to expire
    frappe.db.sql("""
        UPDATE `tabVisitor Log` 
        SET status = 'Checked Out', check_out_time = valid_till
        WHERE status = 'Checked In' 
        AND valid_till < %s
    """, (now_datetime(),))
    
    frappe.db.commit()
