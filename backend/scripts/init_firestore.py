"""
Sahakar Mandal - Firestore Sample Data Initialization Script
Run this script to populate Firestore with demo data for testing
"""

import firebase_admin
from firebase_admin import credentials, firestore, auth
from datetime import datetime, timedelta
import json
import os

# Initialize Firebase
config_path = './firebase-config.json'

if not os.path.exists(config_path):
    print(f"Error: Firebase config not found at {config_path}")
    print("Please create firebase-config.json first")
    exit(1)

cred = credentials.Certificate(config_path)
firebase_admin.initialize_app(cred)
db = firestore.client()

print("=" * 60)
print("Sahakar Mandal - Firestore Data Initialization")
print("=" * 60)

# Sample Users Data
SAMPLE_USERS = [
    {
        'email': 'admin@sahakar.com',
        'password': 'Admin@123456',
        'name': 'Admin User',
        'phone': '9876543210',
        'area': 'Main Area',
        'role': 'admin',
        'status': 'active'
    },
    {
        'email': 'finance@sahakar.com',
        'password': 'Finance@123456',
        'name': 'Rajesh Sharma',
        'phone': '9876543211',
        'area': 'Finance Department',
        'role': 'finance',
        'status': 'active'
    },
    {
        'email': 'collection@sahakar.com',
        'password': 'Collection@123456',
        'name': 'Priya Verma',
        'phone': '9876543212',
        'area': 'Bandra',
        'role': 'collection',
        'status': 'active'
    },
    {
        'email': 'event@sahakar.com',
        'password': 'Event@123456',
        'name': 'Amit Patel',
        'phone': '9876543213',
        'area': 'Events Team',
        'role': 'event',
        'status': 'active'
    },
    {
        'email': 'volunteer@sahakar.com',
        'password': 'Volunteer@123456',
        'name': 'Sneha Desai',
        'phone': '9876543214',
        'area': 'Andheri',
        'role': 'volunteer',
        'status': 'active'
    }
]

# Sample Donations
SAMPLE_DONATIONS = [
    {
        'donation_id': 'DONATION_001',
        'donor_name': 'John Doe',
        'donor_email': 'john@example.com',
        'donor_mobile': '9876543215',
        'amount': 5000,
        'donation_type': 'online',
        'purpose': 'Education',
        'area': 'Bandra',
        'building': 'Tower A',
        'floor': '5',
        'flat': '501',
        'payment_method': 'upi',
        'transaction_id': 'TXN001001',
        'status': 'completed',
        'receipt_generated': True,
        'notes': 'Support for education program',
        'date': datetime.now().isoformat(),
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    },
    {
        'donation_id': 'DONATION_002',
        'donor_name': 'Jane Smith',
        'donor_email': 'jane@example.com',
        'donor_mobile': '9876543216',
        'amount': 10000,
        'donation_type': 'cash',
        'purpose': 'Festival',
        'area': 'Andheri',
        'building': 'Tower B',
        'floor': '3',
        'flat': '301',
        'payment_method': 'cash',
        'transaction_id': '',
        'status': 'completed',
        'receipt_generated': True,
        'notes': 'Support for upcoming festival',
        'date': (datetime.now() - timedelta(days=1)).isoformat(),
        'created_at': (datetime.now() - timedelta(days=1)).isoformat(),
        'updated_at': (datetime.now() - timedelta(days=1)).isoformat()
    },
    {
        'donation_id': 'DONATION_003',
        'donor_name': 'Rajesh Kumar',
        'donor_email': 'rajesh@example.com',
        'donor_mobile': '9876543217',
        'amount': 2500,
        'donation_type': 'check',
        'purpose': 'General',
        'area': 'Powai',
        'building': 'Tower C',
        'floor': '7',
        'flat': '701',
        'payment_method': 'check',
        'transaction_id': 'CHQ001',
        'status': 'pending',
        'receipt_generated': False,
        'notes': 'Cheque donation',
        'date': (datetime.now() - timedelta(days=3)).isoformat(),
        'created_at': (datetime.now() - timedelta(days=3)).isoformat(),
        'updated_at': (datetime.now() - timedelta(days=3)).isoformat()
    },
]

# Sample Expenses
SAMPLE_EXPENSES = [
    {
        'expense_id': 'EXP_001',
        'description': 'Lights and Decorations',
        'amount': 15000,
        'category': 'decoration',
        'event': 'Ganesh Chaturthi',
        'vendor': 'LED Lights Supplier',
        'payment_method': 'cash',
        'receipt_number': 'REC001',
        'status': 'approved',
        'notes': 'LED lights for stage decoration',
        'date': (datetime.now() - timedelta(days=5)).isoformat(),
        'created_at': (datetime.now() - timedelta(days=5)).isoformat(),
        'updated_at': (datetime.now() - timedelta(days=5)).isoformat()
    },
    {
        'expense_id': 'EXP_002',
        'description': 'Prasad Distribution',
        'amount': 8000,
        'category': 'prasad',
        'event': 'Ganesh Chaturthi',
        'vendor': 'Local Sweets Shop',
        'payment_method': 'bank_transfer',
        'receipt_number': 'REC002',
        'status': 'approved',
        'notes': 'Modak and other prasad items',
        'date': (datetime.now() - timedelta(days=4)).isoformat(),
        'created_at': (datetime.now() - timedelta(days=4)).isoformat(),
        'updated_at': (datetime.now() - timedelta(days=4)).isoformat()
    },
    {
        'expense_id': 'EXP_003',
        'description': 'Sound System Rental',
        'amount': 5000,
        'category': 'equipment',
        'event': 'Ganesh Chaturthi',
        'vendor': 'Audio Tech Services',
        'payment_method': 'cash',
        'receipt_number': 'REC003',
        'status': 'approved',
        'notes': 'Microphone and speakers rental',
        'date': (datetime.now() - timedelta(days=3)).isoformat(),
        'created_at': (datetime.now() - timedelta(days=3)).isoformat(),
        'updated_at': (datetime.now() - timedelta(days=3)).isoformat()
    },
]

# Sample Events
SAMPLE_EVENTS = [
    {
        'event_id': 'EVENT_001',
        'title': 'Ganesh Chaturthi Celebration',
        'description': 'Grand annual Ganesh festival celebration with community participation',
        'date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
        'start_time': '18:00',
        'end_time': '22:00',
        'location': 'Community Center, Bandra',
        'category': 'festival',
        'status': 'scheduled',
        'budget': 100000,
        'image_url': '',
        'notes': 'All preparations on track',
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    },
    {
        'event_id': 'EVENT_002',
        'title': 'Diwali Festival',
        'description': 'Festival of lights celebration with special events',
        'date': (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d'),
        'start_time': '19:00',
        'end_time': '23:00',
        'location': 'Community Park, Andheri',
        'category': 'festival',
        'status': 'scheduled',
        'budget': 150000,
        'image_url': '',
        'notes': 'Planning phase',
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    },
    {
        'event_id': 'EVENT_003',
        'title': 'Community Meeting',
        'description': 'Monthly community discussion and planning meeting',
        'date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
        'start_time': '19:00',
        'end_time': '20:30',
        'location': 'Community Hall',
        'category': 'meeting',
        'status': 'scheduled',
        'budget': 5000,
        'image_url': '',
        'notes': 'Monthly gathering',
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    },
]

# Sample Inventory
SAMPLE_INVENTORY = [
    {
        'item_id': 'ITEM_001',
        'name': 'Stage Lights',
        'description': 'LED stage lights for events',
        'category': 'equipment',
        'quantity': 10,
        'unit': 'piece',
        'condition': 'good',
        'location': 'Main Hall Storage',
        'purchase_date': '2023-01-15',
        'cost': 50000,
        'notes': 'Recently serviced',
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    },
    {
        'item_id': 'ITEM_002',
        'name': 'Microphones',
        'description': 'Wireless microphone systems',
        'category': 'equipment',
        'quantity': 5,
        'unit': 'piece',
        'condition': 'good',
        'location': 'Main Hall Storage',
        'purchase_date': '2023-06-20',
        'cost': 25000,
        'notes': 'Working condition',
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    },
    {
        'item_id': 'ITEM_003',
        'name': 'Speakers',
        'description': 'Audio speakers',
        'category': 'equipment',
        'quantity': 4,
        'unit': 'piece',
        'condition': 'fair',
        'location': 'Audio Room',
        'purchase_date': '2022-12-10',
        'cost': 30000,
        'notes': 'Need minor repair',
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    },
]

def create_user_in_firebase(email, password, name):
    """Create user in Firebase Auth"""
    try:
        user = auth.create_user(
            email=email,
            password=password,
            display_name=name
        )
        print(f"✓ Firebase Auth user created: {email} (UID: {user.uid})")
        return user.uid
    except auth.EmailAlreadyExistsError:
        print(f"⚠ User already exists: {email}")
        return None
    except Exception as e:
        print(f"✗ Error creating auth user {email}: {str(e)}")
        return None

def create_users():
    """Create users in Firestore"""
    print("\n" + "=" * 60)
    print("Creating Users...")
    print("=" * 60)
    
    for user_data in SAMPLE_USERS:
        email = user_data['email']
        password = user_data['pop']('password')  # Remove password before saving
        
        # Create in Firebase Auth
        uid = create_user_in_firebase(email, password, user_data['name'])
        
        if uid:
            # Save in Firestore
            user_data['user_id'] = uid
            user_data['created_at'] = datetime.now().isoformat()
            user_data['updated_at'] = datetime.now().isoformat()
            
            db.collection('users').document(uid).set(user_data)
            print(f"✓ Firestore user created: {email}")

def create_donations():
    """Create sample donations"""
    print("\n" + "=" * 60)
    print("Creating Donations...")
    print("=" * 60)
    
    for donation_data in SAMPLE_DONATIONS:
        donation_id = donation_data['donation_id']
        db.collection('donations').document(donation_id).set(donation_data)
        print(f"✓ Created donation: {donation_id}")

def create_expenses():
    """Create sample expenses"""
    print("\n" + "=" * 60)
    print("Creating Expenses...")
    print("=" * 60)
    
    for expense_data in SAMPLE_EXPENSES:
        expense_id = expense_data['expense_id']
        db.collection('expenses').document(expense_id).set(expense_data)
        print(f"✓ Created expense: {expense_id}")

def create_events():
    """Create sample events"""
    print("\n" + "=" * 60)
    print("Creating Events...")
    print("=" * 60)
    
    for event_data in SAMPLE_EVENTS:
        event_id = event_data['event_id']
        db.collection('events').document(event_id).set(event_data)
        print(f"✓ Created event: {event_id}")

def create_inventory():
    """Create sample inventory items"""
    print("\n" + "=" * 60)
    print("Creating Inventory Items...")
    print("=" * 60)
    
    for item_data in SAMPLE_INVENTORY:
        item_id = item_data['item_id']
        db.collection('inventory').document(item_id).set(item_data)
        print(f"✓ Created inventory item: {item_id}")

def main():
    """Main function"""
    try:
        # Create all sample data
        create_users()
        create_donations()
        create_expenses()
        create_events()
        create_inventory()
        
        # Summary
        print("\n" + "=" * 60)
        print("✓ Sample Data Initialization Complete!")
        print("=" * 60)
        print("\nDemo Credentials:")
        print("-" * 60)
        print("Admin:      admin@sahakar.com / Admin@123456")
        print("Finance:    finance@sahakar.com / Finance@123456")
        print("Collection: collection@sahakar.com / Collection@123456")
        print("Event:      event@sahakar.com / Event@123456")
        print("Volunteer:  volunteer@sahakar.com / Volunteer@123456")
        print("-" * 60)
        print("\nYou can now login and test the application!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error during initialization: {str(e)}")
        exit(1)

if __name__ == '__main__':
    main()
