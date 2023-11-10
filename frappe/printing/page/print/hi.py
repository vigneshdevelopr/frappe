import base64
from frappe.utils.pdf import get_pdf


pdfget = get_pdf(docname,doctype)

with open(pdfget, 'rb') as file:
    pdf_base64 = base64.b64encode(file.read()).decode('utf-8')

print(pdf_base64)