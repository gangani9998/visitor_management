import frappe
from frappe.utils import now_datetime, add_days

def run_tests():
    print("\n--- Starting Visitor Log Validation Tests ---\n")
    
    emp = frappe.db.get_value("Employee", {"status": "Active"}, "name")
        
    try:
        print("Test 4: Multiple Entry Logic")
        doc3 = frappe.get_doc({
            "doctype": "Visitor Log",
            "visitor_name": "Test Multiple Entry",
            "number_of_persons": 1,
            "entry_type": "Multiple Entry",
            "status": "Expected",
            "person_to_meet": emp,
            "valid_from": now_datetime(),
            "valid_till": add_days(now_datetime(), 1)
        })
        doc3.insert()
        doc3.reload()
        
        # Change to Checked In
        doc3.status = "Checked In"
        doc3.save()
        
        # Change to Checked Out
        doc3.status = "Checked Out"
        doc3.save()
        
        # Attempt to Check In again (Should Pass for Multiple Entry)
        doc3.status = "Checked In"
        try:
            doc3.save()
            print("✅ PASSED: Successfully allowed Multiple Entry to check back in after checkout.")
        except Exception as e:
            print(f"❌ FAILED: Blocked Multiple Entry incorrectly! Error: {e}")
            
    except Exception as e:
        print(f"❌ FAILED: Unexpected error during Multiple Entry test: {e}")
            
    print("\n--- Tests Complete ---\n")

