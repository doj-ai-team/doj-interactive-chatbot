import json
from flask import Blueprint, render_template
from flask_login import login_required
from views.auth import role_required

workflow_bp = Blueprint('workflow', __name__)

# Mock database of workflows based on SIH SRS requirements
WORKFLOWS = {
    "fir": {
        "title": "Filing an FIR (First Information Report)",
        "description": "A step-by-step guide to reporting a cognizable offense to the police.",
        "steps": [
            "Visit the nearest police station (preferably in the jurisdiction where the offense occurred).",
            "Narrate the incident to the duty officer or hand over a written complaint.",
            "The officer will officially record it in the FIR register.",
            "Carefully read the recorded FIR before signing it.",
            "Demand a free copy of the FIR immediately (It is your legal right)."
        ],
        "documents": [
            "Valid Government ID (Aadhar, Voter ID, Driving License)",
            "Written complaint detailing date, time, location, and sequence of events",
            "Any evidence (photos, videos, medical reports)"
        ],
        "links": [
            {"label": "National Cyber Crime Reporting Portal", "url": "https://cybercrime.gov.in/"},
            {"label": "Know Your Rights (Nyaaya)", "url": "https://nyaaya.org/"}
        ]
    },
    "consumer": {
        "title": "Consumer Complaint Filing",
        "description": "How to file a complaint against defective goods or deficient services.",
        "steps": [
            "Send a formal legal notice to the seller/service provider.",
            "Wait for a response (usually 15-30 days).",
            "If unresolved, draft a consumer complaint detailing the grievance and relief sought.",
            "Attach all relevant evidence (bills, warranty cards, emails).",
            "File the complaint online via edaakhil.nic.in or at the appropriate Consumer Disputes Redressal Commission based on claim value."
        ],
        "documents": [
            "Copy of the Legal Notice sent to the opposing party",
            "Proof of purchase (Invoice, Bill, Receipt)",
            "Warranty/Guarantee cards",
            "Communication records (Emails, Letters, WhatsApp chats)"
        ],
        "links": [
            {"label": "E-Daakhil Portal", "url": "https://edaakhil.nic.in/"},
            {"label": "National Consumer Helpline", "url": "https://consumerhelpline.gov.in/"}
        ]
    },
    "legalaid": {
        "title": "Legal Aid Request",
        "description": "How to apply for free legal services provided by the state.",
        "steps": [
            "Check your eligibility (Women, children, SC/ST, victims of trafficking, and low-income individuals are generally eligible).",
            "Download and fill out the Legal Aid Application Form.",
            "Attach proof of eligibility (e.g., income certificate, caste certificate).",
            "Submit the form to the nearest Legal Services Authority (Taluk, District, State, or Supreme Court level) or apply online through the NALSA portal.",
            "Wait for the authority to assign a panel lawyer to your case."
        ],
        "documents": [
            "Filled Legal Aid Application Form",
            "Proof of Eligibility (Income Certificate, BPL Card, Caste Certificate)",
            "Identity Proof",
            "Summary of the legal issue/case documents"
        ],
        "links": [
            {"label": "NALSA Online Application", "url": "https://nalsa.gov.in/lsams"},
            {"label": "Find Legal Aid Clinics", "url": "https://nalsa.gov.in/"}
        ]
    },
    "land": {
        "title": "Land Dispute Complaint",
        "description": "Initial steps for resolving property or land disputes.",
        "steps": [
            "Gather all ownership documents (Sale deed, Title deed, Khata, Encumbrance certificate).",
            "If it's illegal encroachment, file a police complaint for criminal trespass.",
            "For civil title disputes, consult a lawyer to draft a civil suit.",
            "File the suit in the appropriate civil court having jurisdiction over the property.",
            "Obtain an injunction (stay order) if the other party is trying to alienate or alter the property."
        ],
        "documents": [
            "Original or Certified Copies of Title Deeds/Sale Deeds",
            "Latest Encumbrance Certificate (EC)",
            "Khata Certificate and Extract",
            "Latest Property Tax Receipts",
            "Survey Maps/Sketches"
        ],
        "links": [
            {"label": "eCourts Services", "url": "https://ecourts.gov.in/"},
            {"label": "Bhoomi (Karnataka) / State Land Records Portal", "url": "#"}
        ]
    },
    "domestic": {
        "title": "Domestic Violence Complaint",
        "description": "Filing a complaint under the Protection of Women from Domestic Violence Act, 2005.",
        "steps": [
            "Ensure your immediate safety. If in imminent danger, dial 112 or 1091 (Women's Helpline).",
            "Seek medical help if injured and keep the medical reports.",
            "Report the incident to the nearest police station or a Protection Officer (PO) appointed by the state government.",
            "The PO will assist in making a Domestic Incident Report (DIR) and filing an application before the Magistrate.",
            "You can seek protection orders, residence orders, and monetary relief from the court."
        ],
        "documents": [
            "Medical reports of injuries (if any)",
            "Photographs or evidence of abuse",
            "Marriage certificate or proof of shared household",
            "Any threatening communications"
        ],
        "links": [
            {"label": "NCW Online Complaint", "url": "http://ncwapps.nic.in/onlinecomplaintsv2/frmInstructions.aspx"},
            {"label": "Women Helpline Info", "url": "https://wcd.nic.in/helpline-numbers"}
        ]
    },
    "cyber": {
        "title": "Cybercrime Reporting",
        "description": "Reporting digital fraud, harassment, or data theft.",
        "steps": [
            "Do not delete any evidence (emails, chats, screenshots, bank statements).",
            "Go to the National Cyber Crime Reporting Portal (cybercrime.gov.in).",
            "Register an account and file a complaint online with all gathered evidence.",
            "For financial fraud, immediately call 1930 to freeze the transaction.",
            "Alternatively, visit the nearest local police station's Cyber Cell to file a physical report."
        ],
        "documents": [
            "Screenshots of the incident (URLs, Social Media Profiles, Chats)",
            "Bank statements showing fraudulent transactions",
            "Headers of phishing emails",
            "Any other digital footprint evidence"
        ],
        "links": [
            {"label": "National Cyber Crime Reporting Portal", "url": "https://cybercrime.gov.in/"},
            {"label": "Cyber Safe India", "url": "https://www.cybersafeindia.in/"}
        ]
    }
}

@workflow_bp.route('/workflows')
@workflow_bp.route('/workflows/<workflow_id>')
@login_required
@role_required('Citizen', 'Lawyer', 'Judge', 'Admin')
def workflows(workflow_id=None):
    if not workflow_id or workflow_id not in WORKFLOWS:
        # Default to the first workflow if none selected or invalid
        workflow_id = "fir"
    
    current_workflow = WORKFLOWS[workflow_id]
    
    return render_template('workflow.html', 
                           workflows=WORKFLOWS, 
                           current_id=workflow_id, 
                           current_workflow=current_workflow)
