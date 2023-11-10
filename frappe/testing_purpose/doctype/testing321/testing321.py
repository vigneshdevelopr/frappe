import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class Testing321(Document):
    def on_update(self):
        count_doc = frappe.get_doc("Count-Testing", "counter")
        count_doc.counter += 1
        count_doc.save()
        frappe.msgprint('Hooyah!, Counter Updated Successfully')

    def autoname(self):
        # Define a dictionary mapping options to prefixes
        option_to_Loc = {
            "Thaiyur": "TYR",
            "RF-2": "RF",
            "RP": "RP"
        }

        selected_location = self.location  # Get the location from the document
        locprefix = option_to_Loc.get(selected_location, "Unknown")
        suffix = (frappe.get_doc("Count-Testing", "counter").counter)
        suffix = suffix + 1

        if self.condition:
            prefix = self.department
            self.name = f"AGKL-{prefix}-{locprefix}-{suffix}"
        else:
            self.name = f"AGKL-{locprefix}-{suffix}"
