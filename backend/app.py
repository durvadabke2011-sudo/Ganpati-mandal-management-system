"""
Sahakar Mandal Management System
Backend API using Flask
Author: Development Team
Version: 1.0.0
"""

import os
import json
from datetime import datetime, timedelta
from functools import wraps
from dotenv import load_dotenv

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import firebase_admin
from firebase_admin import credentials, firestore, auth, storage
import jwt
import requests
import qrcode
from io import BytesIO
import hashlib
import uuid
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas

# Load environment variables
load_dotenv()

# Initialize Flask app with static folder for frontend
frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend')
app = Flask(__name__, static_folder=frontend_path, static_url_path='')
app.config['JSON_SORT_KEYS'] = False

# Enable CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Firebase initialization
firebase_config_path = os.getenv('FIREBASE_CONFIG_PATH', './firebase-config.json')

if not os.path.exists(firebase_config_path):
    print(f"Warning: Firebase config file not found at {firebase_config_path}")
    # Use environment variable as fallback
    firebase_config = {
        "type": "service_account",
        "project_id": os.getenv('FIREBASE_PROJECT_ID', ''),
        "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID', ''),
        "private_key": os.getenv('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
        "client_email": os.getenv('FIREBASE_CLIENT_EMAIL', ''),
        "client_id": os.getenv('FIREBASE_CLIENT_ID', ''),
        "auth_uri": os.getenv('FIREBASE_AUTH_URI', 'https://accounts.google.com/o/oauth2/auth'),
        "token_uri": os.getenv('FIREBASE_TOKEN_URI', 'https://oauth2.googleapis.com/token'),
    }
else:
    with open(firebase_config_path) as config_file:
        firebase_config = json.load(config_file)

try:
    # Initialize Firebase only if not already initialized
    try:
        firebase_admin.get_app(name='default')
    except ValueError:
        # App not initialized, initialize it now
        cred = credentials.Certificate(firebase_config)
        firebase_admin.initialize_app(cred, {
            'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET', '')
        })
except Exception as e:
    print(f"Error initializing Firebase: {e}")
    raise

# Initialize Firebase services
db = firestore.client()
firebase_auth = auth
storage_bucket = storage.bucket()

# Configuration
JWT_SECRET = os.getenv('JWT_SECRET', 'sahakar-mandal-secret-key-2024')
RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID', '')
RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET', '')
FIREBASE_WEB_API_KEY = os.getenv('FIREBASE_WEB_API_KEY', '')

# Roles constant
ROLES = {
    'admin': ['admin', 'finance', 'collection', 'event', 'volunteer'],
    'finance': ['finance', 'volunteer'],
    'collection': ['collection', 'volunteer'],
    'event': ['event', 'volunteer'],
    'volunteer': ['volunteer']
}

# ==================== Helper Functions ====================

def generate_token(user_id, role):
    """Generate JWT token for user"""
    payload = {
        'user_id': user_id,
        'role': role,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """Decorator to require valid token"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'message': 'Invalid or expired token'}), 401
        
        return f(payload, *args, **kwargs)
    
    return decorated_function

def role_required(*allowed_roles):
    """Decorator to check role-based access"""
    def decorator(f):
        @wraps(f)
        def decorated_function(payload, *args, **kwargs):
            user_role = payload.get('role', '')
            if user_role not in allowed_roles:
                return jsonify({'message': 'Insufficient permissions'}), 403
            return f(payload, *args, **kwargs)
        return decorated_function
    return decorator

def get_user_document(user_id):
    """Get user document from Firestore"""
    try:
        user_doc = db.collection('users').document(user_id).get()
        if user_doc.exists:
            return user_doc.to_dict()
        return None
    except Exception as e:
        print(f"Error getting user document: {str(e)}")
        return None

def generate_receipt_qr(receipt_id, base_url='http://localhost:5000'):
    """Generate QR code for receipt"""
    receipt_url = f"{base_url}/receipt/{receipt_id}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(receipt_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return img_io

def generate_pdf_receipt(donation_data):
    """Generate PDF receipt using reportlab"""
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        elements = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#FF6B35'),
            spaceAfter=6,
            alignment=1
        )
        
        # Title
        elements.append(Paragraph("सहकार मंडळ", title_style))
        elements.append(Spacer(1, 0.1*inch))
        
        # Donation Receipt Header
        elements.append(Paragraph("दान रसीद (Donation Receipt)", styles['Heading2']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Receipt details table
        receipt_data = [
            ['Receipt ID:', donation_data.get('donation_id', 'N/A')],
            ['Date:', donation_data.get('date', 'N/A')],
            ['Donor Name:', donation_data.get('donor_name', 'Anonymous')],
            ['Email:', donation_data.get('donor_email', 'N/A')],
            ['Mobile:', donation_data.get('donor_mobile', 'N/A')],
        ]
        
        receipt_table = Table(receipt_data, colWidths=[2*inch, 4*inch])
        receipt_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#FFE5CC')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        elements.append(receipt_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Donation details
        elements.append(Paragraph("दान तपशील (Donation Details)", styles['Heading3']))
        elements.append(Spacer(1, 0.1*inch))
        
        donation_amount = donation_data.get('amount', 0)
        donation_type = donation_data.get('donation_type', 'Cash')
        
        donation_details = [
            ['Amount:', f"₹ {donation_amount}"],
            ['Type:', donation_type],
            ['Purpose:', donation_data.get('purpose', 'General')],
            ['Status:', donation_data.get('status', 'Completed')],
        ]
        
        donation_table = Table(donation_details, colWidths=[2*inch, 4*inch])
        donation_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E3F2FD')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        elements.append(donation_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Footer
        elements.append(Paragraph("धन्यवाद! (Thank You!)", styles['Normal']))
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph("सहकार मंडळ | Sahakar Mandal", styles['Normal']))
        
        doc.build(elements)
        buffer.seek(0)
        return buffer
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        return None

# ==================== Frontend Routes ====================

@app.route('/')
def serve_index():
    """Serve the main index page"""
    return send_file(os.path.join(app.static_folder, 'index.html'))

@app.route('/login')
def serve_login():
    """Serve the login page"""
    return send_file(os.path.join(app.static_folder, 'login.html'))

@app.route('/signup')
def serve_signup():
    """Serve the signup page"""
    return send_file(os.path.join(app.static_folder, 'signup.html'))

@app.route('/dashboard')
def serve_dashboard():
    """Serve the dashboard page"""
    return send_file(os.path.join(app.static_folder, 'dashboard.html'))

@app.route('/receipt')
@app.route('/receipt/<receipt_id>')
def serve_receipt(receipt_id=None):
    """Serve the receipt page"""
    return send_file(os.path.join(app.static_folder, 'receipt.html'))

# ==================== Authentication Routes ====================

@app.route('/api/auth/signup', methods=['POST'])
@limiter.limit("5 per minute")
def signup():
    """User registration"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Email and password required'}), 400
        
        email = data.get('email')
        password = data.get('password')
        name = data.get('name', '')
        phone = data.get('phone', '')
        area = data.get('area', '')
        role = data.get('role', 'volunteer')
        
        # Create user in Firebase Auth
        try:
            user = firebase_auth.create_user(
                email=email,
                password=password,
                display_name=name
            )
        except firebase_admin.auth.EmailAlreadyExistsError:
            return jsonify({'message': 'Email already registered'}), 400
        except Exception as e:
            return jsonify({'message': f'Authentication error: {str(e)}'}), 500
        
        # Store user data in Firestore
        user_data = {
            'user_id': user.uid,
            'email': email,
            'name': name,
            'phone': phone,
            'area': area,
            'role': role,
            'status': 'active',
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        db.collection('users').document(user.uid).set(user_data)
        
        # Generate token
        token = generate_token(user.uid, role)
        
        return jsonify({
            'message': 'User registered successfully',
            'user_id': user.uid,
            'token': token,
            'role': role
        }), 201
    
    except Exception as e:
        print(f"Signup error: {str(e)}")
        return jsonify({'message': 'Registration failed'}), 500

@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    """User login"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Email and password required'}), 400
        
        email = data.get('email')
        password = data.get('password')
        
        # Verify user with Firebase REST API
        auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
        
        auth_payload = {
            'email': email,
            'password': password,
            'returnSecureToken': True
        }
        
        try:
            auth_response = requests.post(auth_url, json=auth_payload)
            if auth_response.status_code != 200:
                return jsonify({'message': 'Invalid email or password'}), 401
            
            auth_data = auth_response.json()
            user_id = auth_data.get('localId')
        except Exception as e:
            return jsonify({'message': 'Authentication failed'}), 500
        
        # Get user data from Firestore
        user_data = get_user_document(user_id)
        if not user_data:
            return jsonify({'message': 'User data not found'}), 404
        
        role = user_data.get('role', 'volunteer')
        
        # Generate token
        token = generate_token(user_id, role)
        
        return jsonify({
            'message': 'Login successful',
            'user_id': user_id,
            'token': token,
            'role': role,
            'name': user_data.get('name'),
            'email': user_data.get('email')
        }), 200
    
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'message': 'Login failed'}), 500

@app.route('/api/auth/logout', methods=['POST'])
@token_required
def logout(payload):
    """User logout (token invalidation on client side)"""
    return jsonify({'message': 'Logout successful'}), 200

@app.route('/api/auth/me', methods=['GET'])
@token_required
def get_current_user(payload):
    """Get current user details"""
    try:
        user_id = payload.get('user_id')
        user_data = get_user_document(user_id)
        
        if not user_data:
            return jsonify({'message': 'User not found'}), 404
        
        return jsonify(user_data), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# ==================== Donation Routes ====================

@app.route('/api/donations', methods=['GET'])
@token_required
def get_donations(payload):
    """Get all donations (with filters)"""
    try:
        filters = {}
        
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        if request.args.get('donor_name'):
            filters['donor_name'] = request.args.get('donor_name')
        if request.args.get('area'):
            filters['area'] = request.args.get('area')
        
        query = db.collection('donations')
        
        for key, value in filters.items():
            if key == 'donor_name':
                query = query.where('donor_name', '>=', value)
            else:
                query = query.where(key, '==', value)
        
        docs = query.stream()
        donations = []
        for doc in docs:
            donation = doc.to_dict()
            donation['id'] = doc.id
            donations.append(donation)
        
        return jsonify({
            'message': 'Donations retrieved',
            'count': len(donations),
            'donations': donations
        }), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/donations', methods=['POST'])
@token_required
@role_required('admin', 'finance', 'collection', 'volunteer')
def create_donation(payload):
    """Create new donation"""
    try:
        data = request.get_json()
        
        if not data.get('donor_name') or not data.get('amount'):
            return jsonify({'message': 'Donor name and amount required'}), 400
        
        donation_id = str(uuid.uuid4())
        
        donation_data = {
            'donation_id': donation_id,
            'donor_name': data.get('donor_name'),
            'donor_email': data.get('donor_email', ''),
            'donor_mobile': data.get('donor_mobile', ''),
            'amount': float(data.get('amount', 0)),
            'donation_type': data.get('donation_type', 'cash'),  # cash, online, check
            'purpose': data.get('purpose', 'general'),
            'area': data.get('area', ''),
            'building': data.get('building', ''),
            'floor': data.get('floor', ''),
            'flat': data.get('flat', ''),
            'payment_method': data.get('payment_method', 'cash'),  # cash, upi, card, net_banking
            'transaction_id': data.get('transaction_id', ''),
            'status': data.get('status', 'pending'),  # pending, completed, failed
            'receipt_generated': False,
            'notes': data.get('notes', ''),
            'collected_by': payload.get('user_id'),
            'date': datetime.utcnow().isoformat(),
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        db.collection('donations').document(donation_id).set(donation_data)
        
        return jsonify({
            'message': 'Donation created successfully',
            'donation_id': donation_id,
            'donation': donation_data
        }), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/donations/<donation_id>', methods=['GET'])
@token_required
def get_donation(payload, donation_id):
    """Get specific donation"""
    try:
        doc = db.collection('donations').document(donation_id).get()
        if not doc.exists:
            return jsonify({'message': 'Donation not found'}), 404
        
        donation = doc.to_dict()
        donation['id'] = doc.id
        
        return jsonify(donation), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/donations/<donation_id>', methods=['PUT'])
@token_required
@role_required('admin', 'finance', 'collection', 'volunteer')
def update_donation(payload, donation_id):
    """Update donation"""
    try:
        data = request.get_json()
        
        update_data = {
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # Only allow updating specific fields
        allowed_fields = ['donor_name', 'donor_email', 'donor_mobile', 'amount', 
                        'purpose', 'status', 'notes', 'payment_method', 'transaction_id']
        
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        db.collection('donations').document(donation_id).update(update_data)
        
        return jsonify({
            'message': 'Donation updated successfully',
            'donation_id': donation_id
        }), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/donations/<donation_id>', methods=['DELETE'])
@token_required
@role_required('admin', 'finance')
def delete_donation(payload, donation_id):
    """Delete donation"""
    try:
        db.collection('donations').document(donation_id).delete()
        
        return jsonify({
            'message': 'Donation deleted successfully',
            'donation_id': donation_id
        }), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# ==================== Receipt & QR Code Routes ====================

@app.route('/api/receipts', methods=['GET'])
@token_required
def get_receipts(payload):
    """Get all receipts"""
    try:
        docs = db.collection('receipts').stream()
        receipts = []
        for doc in docs:
            receipt = doc.to_dict()
            receipt['id'] = doc.id
            receipts.append(receipt)
        
        return jsonify({
            'message': 'Receipts retrieved',
            'count': len(receipts),
            'receipts': receipts
        }), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/receipts/<donation_id>/generate', methods=['POST'])
@token_required
@role_required('admin', 'finance', 'collection')
def generate_receipt(payload, donation_id):
    """Generate receipt for donation"""
    try:
        # Get donation data
        doc = db.collection('donations').document(donation_id).get()
        if not doc.exists:
            return jsonify({'message': 'Donation not found'}), 404
        
        donation_data = doc.to_dict()
        
        # Generate receipt
        receipt_id = str(uuid.uuid4())
        
        receipt_data = {
            'receipt_id': receipt_id,
            'donation_id': donation_id,
            'donor_name': donation_data.get('donor_name'),
            'donor_email': donation_data.get('donor_email'),
            'donor_mobile': donation_data.get('donor_mobile'),
            'amount': donation_data.get('amount'),
            'date': donation_data.get('date'),
            'purpose': donation_data.get('purpose'),
            'status': 'active',
            'created_at': datetime.utcnow().isoformat()
        }
        
        db.collection('receipts').document(receipt_id).set(receipt_data)
        
        # Update donation status
        db.collection('donations').document(donation_id).update({
            'receipt_generated': True,
            'receipt_id': receipt_id,
            'status': 'completed',
            'updated_at': datetime.utcnow().isoformat()
        })
        
        return jsonify({
            'message': 'Receipt generated successfully',
            'receipt_id': receipt_id,
            'receipt': receipt_data
        }), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/receipts/<receipt_id>/qrcode', methods=['GET'])
def get_receipt_qrcode(receipt_id):
    """Get QR code for receipt"""
    try:
        # Verify receipt exists
        doc = db.collection('receipts').document(receipt_id).get()
        if not doc.exists:
            return jsonify({'message': 'Receipt not found'}), 404
        
        # Generate QR code
        qr_img = generate_receipt_qr(receipt_id)
        
        return send_file(
            qr_img,
            mimetype='image/png',
            as_attachment=False,
            download_name=f'receipt_{receipt_id}_qr.png'
        )
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/receipts/<receipt_id>/pdf', methods=['GET'])
def get_receipt_pdf(receipt_id):
    """Get PDF for receipt"""
    try:
        # Get receipt data
        doc = db.collection('receipts').document(receipt_id).get()
        if not doc.exists:
            return jsonify({'message': 'Receipt not found'}), 404
        
        receipt_data = doc.to_dict()
        
        # Generate PDF
        pdf_buffer = generate_pdf_receipt(receipt_data)
        
        if pdf_buffer:
            return send_file(
                pdf_buffer,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'receipt_{receipt_id}.pdf'
            )
        else:
            return jsonify({'message': 'Error generating PDF'}), 500
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# ==================== Payment Routes ====================

@app.route('/api/payments/razorpay/order', methods=['POST'])
@token_required
def create_razorpay_order(payload):
    """Create Razorpay order"""
    try:
        data = request.get_json()
        amount = int(float(data.get('amount', 0)) * 100)  # Convert to paise
        
        if amount <= 0:
            return jsonify({'message': 'Invalid amount'}), 400
        
        # Create order using Razorpay API
        razorpay_url = "https://api.razorpay.com/v1/orders"
        
        auth = (RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET)
        order_data = {
            'amount': amount,
            'currency': 'INR',
            'receipt': f"receipt_{datetime.utcnow().timestamp()}",
            'notes': {
                'purpose': data.get('purpose', 'donation'),
                'donor_name': data.get('donor_name', ''),
                'user_id': payload.get('user_id')
            }
        }
        
        try:
            response = requests.post(razorpay_url, json=order_data, auth=auth)
            if response.status_code == 200:
                order = response.json()
                
                # Store order in Firestore
                order_doc = {
                    'order_id': order['id'],
                    'amount': data.get('amount'),
                    'currency': 'INR',
                    'purpose': data.get('purpose', 'donation'),
                    'donor_name': data.get('donor_name', ''),
                    'user_id': payload.get('user_id'),
                    'status': 'created',
                    'created_at': datetime.utcnow().isoformat()
                }
                db.collection('payments').document(order['id']).set(order_doc)
                
                return jsonify({
                    'message': 'Order created successfully',
                    'order_id': order['id'],
                    'amount': data.get('amount'),
                    'currency': 'INR'
                }), 201
            else:
                return jsonify({'message': 'Failed to create order'}), 500
        except Exception as e:
            return jsonify({'message': f'Razorpay error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/payments/razorpay/verify', methods=['POST'])
@token_required
def verify_razorpay_payment(payload):
    """Verify Razorpay payment"""
    try:
        data = request.get_json()
        
        order_id = data.get('order_id')
        payment_id = data.get('payment_id')
        signature = data.get('signature')
        
        # Verify signature
        message = f"{order_id}|{payment_id}"
        hash_signature = hashlib.sha256(
            f"{message}{RAZORPAY_KEY_SECRET}".encode()
        ).hexdigest()
        
        if hash_signature != signature:
            return jsonify({'message': 'Payment signature verification failed'}), 401
        
        # Update payment status in Firestore
        db.collection('payments').document(order_id).update({
            'payment_id': payment_id,
            'status': 'completed',
            'verified_at': datetime.utcnow().isoformat()
        })
        
        # Get payment details to create donation
        payment_doc = db.collection('payments').document(order_id).get()
        if not payment_doc.exists:
            return jsonify({'message': 'Payment not found'}), 404
        
        payment_data = payment_doc.to_dict()
        
        # Create donation record
        donation_id = str(uuid.uuid4())
        donation_data = {
            'donation_id': donation_id,
            'donor_name': payment_data.get('donor_name', 'Anonymous'),
            'amount': payment_data.get('amount'),
            'donation_type': 'online',
            'purpose': payment_data.get('purpose', 'general'),
            'payment_method': 'razorpay',
            'transaction_id': payment_id,
            'status': 'completed',
            'collected_by': payload.get('user_id'),
            'date': datetime.utcnow().isoformat(),
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        db.collection('donations').document(donation_id).set(donation_data)
        
        return jsonify({
            'message': 'Payment verified and donation recorded',
            'donation_id': donation_id,
            'payment_id': payment_id
        }), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/payments/upi/qrcode', methods=['POST'])
@token_required
def generate_upi_qr(payload):
    """Generate UPI QR code"""
    try:
        data = request.get_json()
        amount = data.get('amount', '')
        note = data.get('note', 'Donation')
        
        # UPI format: upi://pay?pa=upi_id&pn=name&am=amount&tn=note
        upi_string = f"upi://pay?pa={os.getenv('UPI_ID', 'admin@upi')}&pn=Sahakar%20Mandal&am={amount}&tn={note}"
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(upi_string)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img_io = BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        
        return send_file(
            img_io,
            mimetype='image/png',
            as_attachment=False,
            download_name=f'upi_qr_{datetime.utcnow().timestamp()}.png'
        )
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# ==================== Expense Routes ====================

@app.route('/api/expenses', methods=['GET'])
@token_required
@role_required('admin', 'finance')
def get_expenses(payload):
    """Get all expenses"""
    try:
        docs = db.collection('expenses').stream()
        expenses = []
        for doc in docs:
            expense = doc.to_dict()
            expense['id'] = doc.id
            expenses.append(expense)
        
        return jsonify({
            'message': 'Expenses retrieved',
            'count': len(expenses),
            'expenses': expenses
        }), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/expenses', methods=['POST'])
@token_required
@role_required('admin', 'finance')
def create_expense(payload):
    """Create new expense"""
    try:
        data = request.get_json()
        
        if not data.get('description') or not data.get('amount'):
            return jsonify({'message': 'Description and amount required'}), 400
        
        expense_id = str(uuid.uuid4())
        
        expense_data = {
            'expense_id': expense_id,
            'description': data.get('description'),
            'amount': float(data.get('amount', 0)),
            'category': data.get('category', 'other'),  # decoration, prasad, utilities, equipment, etc.
            'event': data.get('event', ''),
            'vendor': data.get('vendor', ''),
            'payment_method': data.get('payment_method', 'cash'),
            'receipt_number': data.get('receipt_number', ''),
            'status': data.get('status', 'approved'),  # pending, approved, rejected
            'approved_by': payload.get('user_id') if data.get('status') == 'approved' else '',
            'notes': data.get('notes', ''),
            'date': datetime.utcnow().isoformat(),
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        db.collection('expenses').document(expense_id).set(expense_data)
        
        return jsonify({
            'message': 'Expense created successfully',
            'expense_id': expense_id,
            'expense': expense_data
        }), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/expenses/<expense_id>', methods=['PUT'])
@token_required
@role_required('admin', 'finance')
def update_expense(payload, expense_id):
    """Update expense"""
    try:
        data = request.get_json()
        
        update_data = {
            'updated_at': datetime.utcnow().isoformat()
        }
        
        allowed_fields = ['description', 'amount', 'category', 'event', 'vendor', 
                         'payment_method', 'receipt_number', 'status', 'notes']
        
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        db.collection('expenses').document(expense_id).update(update_data)
        
        return jsonify({
            'message': 'Expense updated successfully',
            'expense_id': expense_id
        }), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/expenses/<expense_id>', methods=['DELETE'])
@token_required
@role_required('admin', 'finance')
def delete_expense(payload, expense_id):
    """Delete expense"""
    try:
        db.collection('expenses').document(expense_id).delete()
        
        return jsonify({
            'message': 'Expense deleted successfully',
            'expense_id': expense_id
        }), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# ==================== Dashboard Analytics Routes ====================

@app.route('/api/dashboard/summary', methods=['GET'])
@token_required
def get_dashboard_summary(payload):
    """Get dashboard summary"""
    try:
        # Get total donations
        donations = db.collection('donations').where('status', '==', 'completed').stream()
        total_donations = 0
        donation_count = 0
        for doc in donations:
            data = doc.to_dict()
            total_donations += data.get('amount', 0)
            donation_count += 1
        
        # Get total expenses
        expenses = db.collection('expenses').where('status', '==', 'approved').stream()
        total_expenses = 0
        for doc in expenses:
            data = doc.to_dict()
            total_expenses += data.get('amount', 0)
        
        balance = total_donations - total_expenses
        
        return jsonify({
            'total_donations': total_donations,
            'total_expenses': total_expenses,
            'balance': balance,
            'donation_count': donation_count,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/dashboard/donations-yearly', methods=['GET'])
@token_required
def get_yearly_donations(payload):
    """Get year-wise donation comparison"""
    try:
        year = request.args.get('year', str(datetime.utcnow().year))
        
        donations = db.collection('donations').where('status', '==', 'completed').stream()
        
        monthly_data = {str(i): 0 for i in range(1, 13)}
        
        for doc in donations:
            data = doc.to_dict()
            donation_date = datetime.fromisoformat(data.get('date', ''))
            
            if str(donation_date.year) == year:
                month = str(donation_date.month)
                monthly_data[month] += data.get('amount', 0)
        
        return jsonify({
            'year': year,
            'monthly_data': monthly_data
        }), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/dashboard/top-donors', methods=['GET'])
@token_required
def get_top_donors(payload):
    """Get leaderboard of top donors"""
    try:
        limit = int(request.args.get('limit', 10))
        
        donations = db.collection('donations').where('status', '==', 'completed').stream()
        
        donor_totals = {}
        for doc in donations:
            data = doc.to_dict()
            donor_name = data.get('donor_name', 'Anonymous')
            amount = data.get('amount', 0)
            
            if donor_name not in donor_totals:
                donor_totals[donor_name] = {'amount': 0, 'count': 0}
            
            donor_totals[donor_name]['amount'] += amount
            donor_totals[donor_name]['count'] += 1
        
        # Sort by amount
        sorted_donors = sorted(
            donor_totals.items(),
            key=lambda x: x[1]['amount'],
            reverse=True
        )[:limit]
        
        leaderboard = [
            {
                'rank': idx + 1,
                'name': donor[0],
                'total_amount': donor[1]['amount'],
                'donation_count': donor[1]['count']
            }
            for idx, donor in enumerate(sorted_donors)
        ]
        
        return jsonify({
            'leaderboard': leaderboard
        }), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# ==================== Event Routes ====================

@app.route('/api/events', methods=['GET'])
def get_events():
    """Get all events"""
    try:
        docs = db.collection('events').stream()
        events = []
        for doc in docs:
            event = doc.to_dict()
            event['id'] = doc.id
            events.append(event)
        
        return jsonify({
            'message': 'Events retrieved',
            'count': len(events),
            'events': events
        }), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/events', methods=['POST'])
@token_required
@role_required('admin', 'event')
def create_event(payload):
    """Create new event"""
    try:
        data = request.get_json()
        
        if not data.get('title') or not data.get('date'):
            return jsonify({'message': 'Title and date required'}), 400
        
        event_id = str(uuid.uuid4())
        
        event_data = {
            'event_id': event_id,
            'title': data.get('title'),
            'description': data.get('description', ''),
            'date': data.get('date'),
            'start_time': data.get('start_time', ''),
            'end_time': data.get('end_time', ''),
            'location': data.get('location', ''),
            'category': data.get('category', 'general'),  # festival, meeting, celebration, etc.
            'status': data.get('status', 'scheduled'),  # scheduled, ongoing, completed, cancelled
            'organizer': payload.get('user_id'),
            'attendees': [],
            'budget': float(data.get('budget', 0)),
            'image_url': data.get('image_url', ''),
            'notes': data.get('notes', ''),
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        db.collection('events').document(event_id).set(event_data)
        
        return jsonify({
            'message': 'Event created successfully',
            'event_id': event_id,
            'event': event_data
        }), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/events/<event_id>', methods=['GET'])
def get_event(event_id):
    """Get specific event"""
    try:
        doc = db.collection('events').document(event_id).get()
        if not doc.exists:
            return jsonify({'message': 'Event not found'}), 404
        
        event = doc.to_dict()
        event['id'] = doc.id
        
        return jsonify(event), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/events/<event_id>', methods=['PUT'])
@token_required
@role_required('admin', 'event')
def update_event(payload, event_id):
    """Update event"""
    try:
        data = request.get_json()
        
        update_data = {
            'updated_at': datetime.utcnow().isoformat()
        }
        
        allowed_fields = ['title', 'description', 'date', 'start_time', 'end_time', 
                         'location', 'category', 'status', 'budget', 'image_url', 'notes']
        
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        db.collection('events').document(event_id).update(update_data)
        
        return jsonify({
            'message': 'Event updated successfully',
            'event_id': event_id
        }), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# ==================== Gallery Routes ====================

@app.route('/api/gallery', methods=['GET'])
def get_gallery():
    """Get gallery images"""
    try:
        event_filter = request.args.get('event')
        
        query = db.collection('gallery')
        if event_filter:
            query = query.where('event_id', '==', event_filter)
        
        docs = query.stream()
        gallery = []
        for doc in docs:
            item = doc.to_dict()
            item['id'] = doc.id
            gallery.append(item)
        
        return jsonify({
            'message': 'Gallery retrieved',
            'count': len(gallery),
            'gallery': gallery
        }), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/gallery', methods=['POST'])
@token_required
@role_required('admin', 'event')
def upload_gallery(payload):
    """Upload gallery item"""
    try:
        if 'file' not in request.files:
            return jsonify({'message': 'No file provided'}), 400
        
        file = request.files['file']
        event_id = request.form.get('event_id', '')
        title = request.form.get('title', '')
        description = request.form.get('description', '')
        
        # Generate unique filename
        filename = f"{event_id}/{uuid.uuid4()}/{file.filename}"
        
        try:
            # Upload to Firebase Storage
            blob = storage_bucket.blob(filename)
            blob.upload_from_string(
                file.read(),
                content_type=file.content_type
            )
            
            # Make public
            blob.make_public()
            url = blob.public_url
        except Exception as e:
            return jsonify({'message': f'Upload failed: {str(e)}'}), 500
        
        # Store metadata in Firestore
        gallery_id = str(uuid.uuid4())
        gallery_data = {
            'gallery_id': gallery_id,
            'event_id': event_id,
            'title': title,
            'description': description,
            'url': url,
            'uploaded_by': payload.get('user_id'),
            'created_at': datetime.utcnow().isoformat()
        }
        
        db.collection('gallery').document(gallery_id).set(gallery_data)
        
        return jsonify({
            'message': 'Gallery item uploaded successfully',
            'gallery_id': gallery_id,
            'url': url
        }), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# ==================== User & Team Management Routes ====================

@app.route('/api/users', methods=['GET'])
@token_required
@role_required('admin')
def get_users(payload):
    """Get all users"""
    try:
        docs = db.collection('users').stream()
        users = []
        for doc in docs:
            user = doc.to_dict()
            user['id'] = doc.id
            # Remove sensitive data
            user.pop('password', None)
            users.append(user)
        
        return jsonify({
            'message': 'Users retrieved',
            'count': len(users),
            'users': users
        }), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/users/<user_id>/role', methods=['PUT'])
@token_required
@role_required('admin')
def update_user_role(payload, user_id):
    """Update user role"""
    try:
        data = request.get_json()
        new_role = data.get('role')
        
        if new_role not in ROLES:
            return jsonify({'message': 'Invalid role'}), 400
        
        db.collection('users').document(user_id).update({
            'role': new_role,
            'updated_at': datetime.utcnow().isoformat()
        })
        
        return jsonify({
            'message': 'User role updated successfully',
            'user_id': user_id,
            'role': new_role
        }), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# ==================== Inventory Routes ====================

@app.route('/api/inventory', methods=['GET'])
@token_required
def get_inventory(payload):
    """Get inventory items"""
    try:
        docs = db.collection('inventory').stream()
        items = []
        for doc in docs:
            item = doc.to_dict()
            item['id'] = doc.id
            items.append(item)
        
        return jsonify({
            'message': 'Inventory retrieved',
            'count': len(items),
            'items': items
        }), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/inventory', methods=['POST'])
@token_required
@role_required('admin', 'event')
def create_inventory_item(payload):
    """Create inventory item"""
    try:
        data = request.get_json()
        
        if not data.get('name') or not data.get('quantity'):
            return jsonify({'message': 'Name and quantity required'}), 400
        
        item_id = str(uuid.uuid4())
        
        item_data = {
            'item_id': item_id,
            'name': data.get('name'),
            'description': data.get('description', ''),
            'category': data.get('category', 'equipment'),  # lights, speakers, equipment, etc.
            'quantity': int(data.get('quantity', 0)),
            'unit': data.get('unit', 'piece'),
            'condition': data.get('condition', 'good'),  # good, fair, poor
            'location': data.get('location', ''),
            'purchase_date': data.get('purchase_date', ''),
            'cost': float(data.get('cost', 0)),
            'notes': data.get('notes', ''),
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        db.collection('inventory').document(item_id).set(item_data)
        
        return jsonify({
            'message': 'Inventory item created successfully',
            'item_id': item_id,
            'item': item_data
        }), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# ==================== Health Check Route ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'Sahakar Mandal API'
    }), 200

# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'message': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'message': 'Internal server error'}), 500

if __name__ == '__main__':
    # Get environment variables
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('FLASK_PORT', 5000))
    
    print(f"""
    ╔════════════════════════════════════════════════╗
    ║     Sahakar Mandal Management System           ║
    ║              Backend API Server                ║
    ║              Version: 1.0.0                    ║
    ╚════════════════════════════════════════════════╝
    """)
    
    app.run(debug=debug, host='0.0.0.0', port=port)
