# Firebase Setup Guide

Complete guide to setup Firebase for Sahakar Mandal.

## Prerequisites

- Google Account
- Web browser
- Text editor

## Step 1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click **"Create a project"**
3. Enter project name: `sahakar-mandal`
4. Accept terms and click **"Create project"**
5. Wait for project creation (2-3 minutes)

## Step 2: Enable Firestore Database

1. In Firebase Console, go to **Build** → **Firestore Database**
2. Click **"Create database"**
3. Select region: **India (asia-south1)** or closest to you
4. **Start in test mode** (change to production later)
5. Click **"Enable"**

### Firestore Collections Structure

Create the following collections in Firestore:

```
sahakar-mandal/
├── users/              # User data
│   └── {user_id}
│       ├── email
│       ├── name
│       ├── role
│       └── ...
├── donations/          # Donation records
│   └── {donation_id}
│       ├── amount
│       ├── donor_name
│       └── ...
├── receipts/           # Receipt data
│   └── {receipt_id}
│       ├── donation_id
│       ├── amount
│       └── ...
├── expenses/           # Expense tracking
│   └── {expense_id}
│       ├── amount
│       ├── category
│       └── ...
├── events/             # Event management
│   └── {event_id}
│       ├── title
│       ├── date
│       └── ...
├── gallery/            # Image metadata
│   └── {gallery_id}
│       ├── url
│       ├── title
│       └── ...
├── inventory/          # Inventory items
│   └── {item_id}
│       ├── name
│       ├── quantity
│       └── ...
└── payments/           # Payment records
    └── {payment_id}
        ├── amount
        ├── status
        └── ...
```

## Step 3: Enable Authentication

1. Go to **Build** → **Authentication**
2. Click **"Get started"**
3. Select **Email/Password**
4. Enable and click **"Save"**
5. Optionally enable Google Sign-In:
   - Click **"Google"**
   - Add support email
   - Save

## Step 4: Create Storage Bucket

1. Go to **Build** → **Storage**
2. Click **"Get started"**
3. Select region: **Asia (asia-south1)** or closest
4. Choose **"Test mode"** initially
5. Create bucket

### Storage Rules

Update storage rules for security:

```
rules_version = '2';

service firebase.storage {
  match /b/{bucket}/o {
    // Gallery images - public read, authenticated write
    match /gallery/{allPaths=**} {
      allow read: if true;
      allow write: if request.auth != null;
    }
    
    // User uploads - authenticated only
    match /uploads/{userId}/{allPaths=**} {
      allow read, write: if request.auth.uid == userId;
    }
  }
}
```

## Step 5: Get Service Account Key

1. Go to **Project Settings** (gear icon)
2. Click **"Service Accounts"** tab
3. Click **"Generate New Private Key"**
4. Save JSON file as `firebase-config.json`
5. Keep this file **PRIVATE** and add to `.gitignore`

**File location**: `backend/firebase-config.json`

```json
{
  "type": "service_account",
  "project_id": "sahakar-mandal-xxxxx",
  "private_key_id": "xxxxxxxxx",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...",
  "client_email": "firebase-adminsdk-xxxxx@sahakar-mandal-xxxxx.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/..."
}
```

## Step 6: Get Web API Key

1. Go to **Project Settings** → **General**
2. Copy **Web API Key** from "Your apps" section
3. Add to `.env`:
   ```
   FIREBASE_WEB_API_KEY=AIzaSyD...
   ```

## Step 7: Configure Firestore Rules

1. Go to **Firestore Database** → **Rules**
2. Replace with:

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users - own data only
    match /users/{userId} {
      allow read, write: if request.auth.uid == userId;
      allow read: if request.auth.uid != null && 
                     get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'admin';
    }
    
    // Donations - authenticated users, admins can read all
    match /donations/{document=**} {
      allow create, update, delete: if request.auth.uid != null && 
        (get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role in ['admin', 'finance', 'collection']);
      allow read: if request.auth.uid != null;
    }
    
    // Receipts - view only for donors, edit for admins
    match /receipts/{document=**} {
      allow read: if request.auth.uid != null;
      allow create, update, delete: if request.auth.uid != null &&
        get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role in ['admin', 'finance'];
    }
    
    // Expenses - finance team only
    match /expenses/{document=**} {
      allow read, write: if request.auth.uid != null &&
        get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role in ['admin', 'finance'];
    }
    
    // Events - event team and admins
    match /events/{document=**} {
      allow read: if true;
      allow create, update, delete: if request.auth.uid != null &&
        get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role in ['admin', 'event'];
    }
    
    // Gallery - public read
    match /gallery/{document=**} {
      allow read: if true;
      allow create, update, delete: if request.auth.uid != null &&
        get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role in ['admin', 'event'];
    }
    
    // Inventory - event team
    match /inventory/{document=**} {
      allow read: if request.auth.uid != null;
      allow create, update, delete: if request.auth.uid != null &&
        get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role in ['admin', 'event'];
    }
    
    // Payments - finance team
    match /payments/{document=**} {
      allow read, write: if request.auth.uid != null &&
        get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role in ['admin', 'finance'];
    }
  }
}
```

3. Click **"Publish"**

## Step 8: Initialize Database with Sample Data

Run this script to populate sample data:

```python
# backend/scripts/init_firestore.py

import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

cred = credentials.Certificate('./firebase-config.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Sample users
users = [
    {
        'name': 'Admin User',
        'email': 'admin@sahakar.com',
        'role': 'admin',
        'phone': '9876543210',
        'area': 'Main',
        'status': 'active'
    },
    {
        'name': 'Finance User',
        'email': 'finance@sahakar.com',
        'role': 'finance',
        'phone': '9876543211',
        'area': 'Finance',
        'status': 'active'
    },
    {
        'name': 'Volunteer User',
        'email': 'volunteer@sahakar.com',
        'role': 'volunteer',
        'phone': '9876543212',
        'area': 'Bandra',
        'status': 'active'
    }
]

# Add users to Firestore
for user in users:
    db.collection('users').add(user)
    print(f"Created user: {user['email']}")

print("Database initialization complete!")
```

## Step 9: Create Demo Events

```python
events = [
    {
        'title': 'Ganesh Chaturthi Celebration',
        'description': 'Annual Ganesh festival celebration',
        'date': '2024-09-07',
        'location': 'Community Center',
        'budget': 100000,
        'status': 'scheduled'
    },
    {
        'title': 'Diwali Festival',
        'description': 'Grand Diwali celebration',
        'date': '2024-11-01',
        'location': 'Community Park',
        'budget': 150000,
        'status': 'scheduled'
    }
]

for event in events:
    db.collection('events').add(event)
    print(f"Created event: {event['title']}")
```

## Step 10: Environment Setup

Create `.env` file in backend directory:

```env
# Firebase Configuration
FIREBASE_PROJECT_ID=sahakar-mandal-xxxxx
FIREBASE_PRIVATE_KEY_ID=xxxxxxxxx
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@sahakar-mandal-xxxxx.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=123456789
FIREBASE_STORAGE_BUCKET=sahakar-mandal-xxxxx.appspot.com
FIREBASE_WEB_API_KEY=AIzaSyD...

# Other Configuration
JWT_SECRET=your-secret-key-here
RAZORPAY_KEY_ID=rzp_test_xxxxx
RAZORPAY_KEY_SECRET=your_secret_here
UPI_ID=admin@upi
```

## Frontend Firebase Config

Update frontend Firebase config in HTML:

```javascript
// frontend/js/config.js

const FIREBASE_CONFIG = {
    apiKey: "AIzaSyDk....",
    authDomain: "sahakar-mandal-xxxxx.firebaseapp.com",
    projectId: "sahakar-mandal-xxxxx",
    storageBucket: "sahakar-mandal-xxxxx.appspot.com",
    messagingSenderId: "123456789",
    appId: "1:123456789:web:abcdef123456",
    measurementId: "G-XXXXXX"
};
```

## Security Checklist

- [ ] Firebase service account key is in `.gitignore`
- [ ] Firestore rules are restrictive
- [ ] Storage rules allow public read for gallery
- [ ] Authentication email/password enabled
- [ ] All sensitive keys in `.env` file
- [ ] `.env` file is not committed to Git
- [ ] CORS configured for backend

## Testing Firebase Connection

```bash
cd backend
python -c "
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate('firebase-config.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Test write
db.collection('test').add({'message': 'Connection successful'})

# Test read
docs = db.collection('test').stream()
for doc in docs:
    print(f'Test document: {doc.to_dict()}')

print('Firebase connection successful!')
"
```

## Troubleshooting

### Connection Error
```
Error: "Could not determine credentials"
Solution: 
- Check firebase-config.json path
- Ensure FIREBASE_CONFIG_PATH in .env
```

### Permission Denied
```
Error: "Missing or insufficient permissions"
Solution:
- Update Firestore rules
- Check user role in Firestore
- Ensure user is authenticated
```

### Storage Upload Fails
```
Error: "Storage bucket not configured"
Solution:
- Enable Firebase Storage
- Update FIREBASE_STORAGE_BUCKET in .env
- Check storage rules
```

## Monitoring & Analytics

1. **Firestore Usage**:
   - Go to **Firestore Database** → **Usage**
   - Monitor reads/writes/deletes

2. **Authentication**:
   - Go to **Authentication** → **Usage**
   - Monitor signups/logins

3. **Storage**:
   - Go to **Storage** → **Usage**
   - Monitor upload/download bandwidth

## Production Deployment

Before going live:

1. Change Firestore from **Test Mode** to **Production Mode**
2. Update security rules for production
3. Enable backup
4. Set up Cloud Monitoring
5. Configure billing alerts
6. Enable Cloud Logging

## References

- [Firebase Documentation](https://firebase.google.com/docs)
- [Firestore Documentation](https://firebase.google.com/docs/firestore)
- [Firebase Authentication](https://firebase.google.com/docs/auth)
- [Firebase Storage](https://firebase.google.com/docs/storage)

---

Last Updated: 2024
Version: 1.0.0
