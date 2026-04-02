import json
import os
from collections import Counter
from flask import Blueprint, render_template
from flask_login import login_required
from views.auth import role_required

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics')
@login_required
@role_required('Admin')
def dashboard():
    # In a real app, this would query a database. 
    # For AskLegal.ai using Redis, we check the query logs (or a mock representation)
    
    # Mock data for DOJ Analytics demonstrating Hierarchical Clusters
    query_categories = {
        "Criminal Law - Cyber Fraud": 245,
        "Criminal Law - Theft & Robbery": 182,
        "Civil Law - Property Dispute": 312,
        "Civil Law - Contract Breach": 89,
        "Consumer Law - Service Deficiency": 210,
        "Criminal Law - Domestic Violence": 154
    }
    
    # Top accessed IPC Sections (Mocked)
    top_ipc = {
        "Section 420 (Cheating)": 88,
        "Section 378 (Theft)": 65,
        "Section 498A (Cruelty by Husband/Relatives)": 52,
        "Section 503 (Criminal Intimidation)": 41
    }
    
    # Total Queries Processed
    total_queries = sum(query_categories.values())
    
    return render_template('analytics.html', 
                           categories=query_categories, 
                           top_ipc=top_ipc,
                           total_queries=total_queries)
