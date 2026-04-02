import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import logging
import sys
import time
from functools import wraps
from flask import Flask, request, jsonify, render_template, send_from_directory, g, redirect, url_for, flash, abort, session
from flask_login import LoginManager, current_user, login_required
import uuid
from views.auth import role_required
from models import db, User, PendingSubmission

try:
    from views.chatbotLegalv2 import process_input, create_new_chat, get_chat_list, load_chat, delete_chat_record
except Exception as e:
    print(f"❌ Failed to import chatbotLegalv2: {e}", file=sys.stderr)
    raise
try:
    from views.judgmentPred import extract_text_from_file, analyze_case
except Exception as e:
    print(f"❌ Failed to import judgementPred: {e}", file=sys.stderr)
    raise
try:
    from views.docGen import generate_legal_document
except Exception as e:
    print(f"❌ Failed to import docGen: {e}", file=sys.stderr)
    raise
try:
    from views.complaintAnalyzer import analyze_complaint
except Exception as e:
    print(f"❌ Failed to import complaintAnalyzer: {e}", file=sys.stderr)
    raise
try:
    from views.analytics import analytics_bp
except Exception as e:
    print(f"❌ Failed to import analytics_bp: {e}", file=sys.stderr)
    raise
try:
    from views.workflow import workflow_bp
except Exception as e:
    print(f"❌ Failed to import workflow_bp: {e}", file=sys.stderr)
    raise
try:
    from views.auth import auth_bp
except Exception as e:
    print(f"❌ Failed to import auth_bp: {e}", file=sys.stderr)
    raise

print("Starting Flask app...", file=sys.stderr)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'justice-secret-key-deploy')

# Max file size 16MB
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

rate_limit_store = {}

def rate_limit(limit_requests, per_seconds):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            ip = request.remote_addr
            now = time.time()
            if ip not in rate_limit_store:
                rate_limit_store[ip] = []
            rate_limit_store[ip] = [t for t in rate_limit_store[ip] if now - t < per_seconds]
            if len(rate_limit_store[ip]) >= limit_requests:
                return jsonify({"error": "Rate limit exceeded. Please try again later."}), 429
            rate_limit_store[ip].append(now)
            return f(*args, **kwargs)
        return wrapped
    return decorator

# Configure SQLite Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///justice.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Configure Login Manager
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(analytics_bp)
app.register_blueprint(workflow_bp)
app.register_blueprint(auth_bp, url_prefix='/auth')

# Automatically create database tables if they don't exist
with app.app_context():
    db.create_all()
    if not User.query.filter_by(role='Admin').first():
        try:
            admin = User(username='admin', email='admin@doj.gov.in', role='Admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Created default admin user: admin@doj.gov.in / admin123")
        except Exception as e:
            db.session.rollback()
            print(f"Failed to create default admin: {e}")

# Clear any existing handlers
for handler in app.logger.handlers:
    app.logger.removeHandler(handler)

# Configure Flask logger to output INFO level to console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
console_handler.setFormatter(formatter)

app.logger.addHandler(console_handler)
app.logger.setLevel(logging.INFO)

from datetime import datetime, timedelta

def group_chats_by_recency(chats):
    groups = {
        "Today": [],
        "Yesterday": [],
        "Previous 7 Days": [],
        "30 Days": []
    }
    
    now = datetime.now()
    today = now.date()
    yesterday = today - timedelta(days=1)
    seven_days = today - timedelta(days=7)
    thirty_days = today - timedelta(days=30)

    for chat in chats:
        updated_str = chat.get("updated_at", "")
        if not updated_str: 
            groups["30 Days"].append(chat)
            continue
            
        try:
            updated_dt = datetime.fromisoformat(updated_str).date()
            if updated_dt == today:
                groups["Today"].append(chat)
            elif updated_dt == yesterday:
                groups["Yesterday"].append(chat)
            elif updated_dt >= seven_days:
                groups["Previous 7 Days"].append(chat)
            elif updated_dt >= thirty_days:
                groups["30 Days"].append(chat)
            else:
                groups["30 Days"].append(chat) # fallback to oldest shown category
        except:
             groups["30 Days"].append(chat)
             
    # Clean up empty groups
    return {k: v for k, v in groups.items() if v}


@app.route('/')
def index():
    if current_user.is_authenticated:
        user_id = current_user.id
    else:
        # Lazy Registration: Assign a temporary guest UUID
        if 'guest_id' not in session:
            session['guest_id'] = str(uuid.uuid4())
        user_id = session['guest_id']

    requested_chat = request.args.get('chat')
    chats = get_chat_list(user_id)

    if requested_chat and any(c.get("id") == requested_chat for c in chats):
        chat_name = requested_chat
    elif chats:
        chat_name = chats[0]["id"]
    else:
        chat_name = create_new_chat(user_id)
        chats = get_chat_list(user_id)  # Re-fetch so the new chat shows in the sidebar immediately!
        
    chat_groups = group_chats_by_recency(chats)
    chat_data = load_chat(chat_name)

    return render_template('index.html', chat_name=chat_name, chat_groups=chat_groups, chat_data=chat_data)

@app.route('/chat_list')
def chat_list():
    if current_user.is_authenticated:
        user_id = current_user.id
    else:
        user_id = session.get('guest_id')
        if not user_id: return jsonify({"chat_groups": {}})

    chats = get_chat_list(user_id)
    chat_groups = group_chats_by_recency(chats)
    return jsonify({"chat_groups": chat_groups})

@app.route('/delete_chat/<chat_id>', methods=['DELETE'])
def delete_chat(chat_id):
    success = delete_chat_record(chat_id)
    return jsonify({"success": success})


@app.route('/chat', methods=['POST'])
@rate_limit(15, 60)
def chat():
    data = request.json
    user_input = data.get('user_input', '')
    chat_name = data.get('chat_name', '')
    language = data.get('language', 'English')

    if not user_input or not chat_name:
        return jsonify({"error": "Missing input or chat name"}), 400

    # Get response, source, and confidence
    response, source_type, low_confidence, citations = process_input(chat_name, user_input, language=language, return_source=True)

    # Log the source explicitly
    app.logger.info(f"⚡ Answer Source: {source_type} | Low Confidence: {low_confidence} | Citations: {len(citations)} | Chat: {chat_name}")

    return jsonify({
        "response": response,
        "source": source_type,
        "low_confidence": low_confidence,
        "citations": citations
    })

@app.route('/new_chat', methods=['POST'])
def new_chat():
    if current_user.is_authenticated:
        user_id = current_user.id
    else:
        user_id = session.get('guest_id')
        if not user_id:
            session['guest_id'] = str(uuid.uuid4())
            user_id = session['guest_id']
    
    chat_name = create_new_chat(user_id)
    return jsonify({"chat_name": chat_name})

@app.route('/load_chat', methods=['POST'])
def load_existing_chat():
    data = request.json
    chat_name = data.get('chat_name')
    if not chat_name:
        return jsonify({"error": "Chat name required"}), 400

    chat_data = load_chat(chat_name)
    return jsonify({"chat_data": chat_data})

@app.route('/predict', methods=['GET', 'POST'])
@login_required
@role_required('Lawyer', 'Judge', 'Admin')
@rate_limit(5, 60)
def predict_judgment():
    chats = get_chat_list()
    chat_groups = group_chats_by_recency(chats)

    error = None
    text = ""
    result = None

    if request.method == 'POST':
        file = request.files.get('file')
        file_type = request.form.get('file_type')

        if not file or not file_type:
            return jsonify({"error": "File and file type required."}), 400

        temp_dir = os.path.join(os.getcwd(), 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, file.filename)
        file.save(temp_path)

        try:
            text = extract_text_from_file(temp_path, file_type)
            result = analyze_case(text)
            return jsonify({
                "text": text,
                "result": result
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            try:
                os.remove(temp_path)
            except:
                pass

    # For GET request: render page
    return render_template('predict.html', chat_groups=chat_groups)

@app.route('/complaint', methods=['GET', 'POST'])
@login_required
@role_required('Citizen', 'Lawyer', 'Judge', 'Admin')
@rate_limit(5, 60)
def handle_complaint():
    chats = get_chat_list()
    chat_groups = group_chats_by_recency(chats)

    error = None
    text = ""
    result = None

    if request.method == 'POST':
        file = request.files.get('file')
        file_type = request.form.get('file_type')

        if not file or not file_type:
            return jsonify({"error": "File and file type required."}), 400

        temp_dir = os.path.join(os.getcwd(), 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, file.filename)
        file.save(temp_path)

        try:
            text = extract_text_from_file(temp_path, file_type)
            result = analyze_complaint(text)
            return jsonify({
                "text": text,
                "result": result
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            try:
                os.remove(temp_path)
            except:
                pass

    # For GET request: render page
    return render_template('complaint.html', chat_groups=chat_groups)


@app.route('/generate')
@login_required
@role_required('Lawyer', 'Judge', 'Admin')
def generate():
    chats = get_chat_list()
    chat_groups = group_chats_by_recency(chats)
    return render_template('generate.html', chat_groups=chat_groups)

@app.route('/generate_document', methods=['POST'])
@login_required
@role_required('Lawyer', 'Judge', 'Admin')
@rate_limit(5, 60)
def generate_document():
    data = request.json
    prompt = data.get('doc_prompt', '')
    if not prompt:
        return jsonify({'error': 'Prompt required'}), 400

    try:
        file_path, file_name = generate_legal_document(prompt)
        return jsonify({
            'download_url': f'/download/{file_name}',
            'file_name': file_name
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory('static/generated_docs', filename, as_attachment=True)

@app.route('/submit_suggestion', methods=['POST'])
@rate_limit(5, 60)
def submit_suggestion():
    data = request.json
    query = data.get('query')
    suggestion = data.get('suggestion')
    source = data.get('source', '')

    if not query or not suggestion:
        return jsonify({"error": "Query and suggestion are required."}), 400

    new_sub = PendingSubmission(query=query, suggested_answer=suggestion, source=source)
    db.session.add(new_sub)
    db.session.commit()
    return jsonify({"success": True, "message": "Suggestion submitted for review."})

@app.route('/admin/pending', methods=['GET'])
@login_required
@role_required('Admin', 'Judge')
def view_pending():
    pending = PendingSubmission.query.filter_by(status='PENDING').all()
    # For now, just return JSON; will integrate into analytics UI later
    return jsonify([{
        "id": p.id,
        "query": p.query,
        "suggestion": p.suggested_answer,
        "source": p.source,
        "created_at": p.created_at.isoformat()
    } for p in pending])

@app.route('/admin/approve/<int:sub_id>', methods=['POST'])
@login_required
@role_required('Admin', 'Judge')
def approve_suggestion(sub_id):
    data = request.json
    action = data.get('action') # 'approve' or 'reject'
    
    sub = PendingSubmission.query.get_or_404(sub_id)
    
    if action == 'approve':
        sub.status = 'APPROVED'
        # Logic to update laws_raw.json
        try:
            laws_file = 'laws_raw.json'
            with open(laws_file, 'r', encoding='utf-8') as f:
                laws_data = json.load(f)
            
            if "Crowdsourced" not in laws_data:
                laws_data["Crowdsourced"] = {}
            
            entry_id = f"SUGGEST_{sub.id}"
            laws_data["Crowdsourced"][entry_id] = {
                "title": f"Verified User Suggestion: {sub.query[:50]}",
                "content": sub.suggested_answer,
                "source": sub.source
            }
            
            with open(laws_file, 'w', encoding='utf-8') as f:
                json.dump(laws_data, f, indent=2)
            
            # Rebuild index (async or immediate)
            from views.chatbotLegalv2 import build_faiss_index
            build_faiss_index()
            
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Failed to update KB: {str(e)}"}), 500
            
    elif action == 'reject':
        sub.status = 'REJECTED'
    
    db.session.commit()
    return jsonify({"success": True, "message": f"Suggestion {action}d."})

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # Run server without debug reloader to prevent ML memory crashes
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
