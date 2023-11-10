import frappe
import pydocusign
import hashlib
import os
import uuid
from frappe.utils.pdf import get_pdf
from frappe.printing.doctype.print_format.print_format import download_pdf
import base64
from frappe.www.printview import get_print_format_doc
import requests

from docusign_esign.client.api_client import ApiClient
from docusign_esign.client.auth.oauth import OAuth

@frappe.whitelist()
def get_print_settings_to_show(doctype, docname):
    doc = frappe.get_doc(doctype, docname)
    print_settings = frappe.get_single("Print Settings")

    if hasattr(doc, "get_print_settings"):
        fields = doc.get_print_settings() or []
    else:
        return []

    print_settings_fields = []
    for fieldname in fields:
        df = print_settings.meta.get_field(fieldname)
        if not df:
            continue
        df.default = print_settings.get(fieldname)
        print_settings_fields.append(df)

    return print_settings_fields

from docusign_esign import EnvelopesApi, RecipientViewRequest, Document, Signer, EnvelopeDefinition, SignHere, Tabs, Recipients

@frappe.whitelist()
def initiate_docusign(docname, doctype):
    try:
        
        account_id = "d7924630-06a5-4e73-be71-1f5c50068886"
        base_path = "https://demo.docusign.net/restapi" 
        refresh_token_document = frappe.get_doc('DocuSign', 'Refresh_Token')
        refresh_token = refresh_token_document.values
        frappe.msgprint(refresh_token)
        pattern = "/Please_sign_here/"  
        signer_client_id = "53be8fd1-748e-4bc7-9d72-5c971a20478f"  
        signer_name = "Vignesh G"
        signer_email = "vigneshwebdevelopr@gmail.com"
        signer_secret = '28a31fa1-b30b-4161-ae76-10442499310b'

        token_url = 'https://account-d.docusign.com/oauth/token' 

        data =  {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': signer_client_id,
            'client_secret': signer_secret
    
        }

        

        new_access_token = ""  
        new_refresh_token = ""  

        response = requests.post(token_url, data=data)
        if response.status_code == 200:
            token_data = response.json()
            new_access_token = token_data["access_token"]
            new_refresh_token = token_data["refresh_token"]
            frappe.msgprint('Token refreshed successfully!')
        else:
            frappe.msgprint('Token refresh failed!')

        if new_access_token:
            access_token_document = frappe.get_doc('DocuSign', 'Access_Token')
            access_token_document.values = new_access_token
            access_token_document.save()

        if new_refresh_token:
            refresh_token_document.values = new_refresh_token
            refresh_token_document.save()

      
      
        html_content = frappe.get_print(doctype, docname, as_pdf=True,print_format='purchase_order_format')

        # pdf_data = get_pdf(html_content)

        pdf_base64 = base64.b64encode(html_content).decode('utf-8')

        document = Document(
            document_base64=pdf_base64,
            name="AGKL-TEST document",
            file_extension="pdf",
            document_id=1,
        )

        envelope_definition = make_envelope(
            signer_name, signer_email, pattern, signer_client_id, document
        )

        api_client = create_api_client(base_path, new_access_token)

        envelope_api = EnvelopesApi(api_client)
        results = envelope_api.create_envelope(account_id, envelope_definition=envelope_definition)

        envelope_id = results.envelope_id

        recipient_view_request = RecipientViewRequest(
            authentication_method="email",
            client_user_id=signer_client_id,
            recipient_id="1",
            return_url=frappe.utils.get_url("http://127.0.0.1:8000/app"), 
            user_name=signer_name,
            email=signer_email,
            auto_download="true"
        )

        results = envelope_api.create_recipient_view(account_id, envelope_id, recipient_view_request=recipient_view_request)
        signing_url = results.url

        return {"redirect_url": signing_url}

    except Exception as e:
        frappe.msgprint(f'Error: {str(e)}')
        return None

# Rest of your code...


def create_api_client(base_path, access_token):
    api_client = ApiClient()
    api_client.host = base_path
    api_client.set_default_header("Authorization", f"Bearer {access_token}")
    return api_client

def make_envelope(signer_name, signer_email, pattern, signer_client_id, document):
    signer = Signer(
        email=signer_email,
        name=signer_name,
        recipient_id="1",
        routing_order="1",
        client_user_id=signer_client_id
    )

    sign_here = SignHere(
        anchor_string=pattern,
        anchor_units="pixels",
        anchor_y_offset="10",
        anchor_x_offset="20"
    )

    signer.tabs = Tabs(sign_here_tabs=[sign_here])

    envelope_definition = EnvelopeDefinition(
        email_subject="Document from AGNIKUL-TEST, SIGN THE DOCUMENT ASAP",
        documents=[document],
        recipients=Recipients(signers=[signer]),
        status="sent"
    )

    return envelope_definition