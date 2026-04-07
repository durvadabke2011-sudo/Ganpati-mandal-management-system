# Sahakar Mandal - Complete Installation Guide

Step-by-step guide to install and run Sahakar Mandal locally.

## Prerequisites

Before starting, ensure you have:

- **Python 3.9+** - [Download](https://www.python.org/downloads/)
- **Git** - [Download](https://git-scm.com/download)
- **Google Account** - For Firebase
- **Text Editor** - VS Code, Sublime, or similar
- **Modern Web Browser** - Chrome, Firefox, Safari, Edge

### Verify Installations

```bash
python --version
# Python 3.9.0 or higher

git --version
# git version 2.x.x

pip --version
# pip 21.x.x or higher
```

---

## Step 1: Clone/Download Project

### Option A: Git Clone (Recommended)

```bash
# Clone repository
git clone https://github.com/yourusername/sahakar-mandal.git

# Navigate to project
cd sahakar-mandal-project
```

### Option B: Download ZIP

1. Download as ZIP from GitHub
2. Extract to your desired location
3. Open terminal/command prompt in project folder

---

## Step 2: Firebase Setup

### Step 2.1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click **"Create a project"**
3. Enter: `sahakar-mandal`
4. Accept terms → **"Create project"**
5. Wait 2-3 minutes for project creation

### Step 2.2: Enable Firestore Database

1. In Firebase Console, click **Build** → **Firestore Database**
2. Click **"Create database"**
3. Select region: **India (asia-south1)**
4. Start in **"Test mode"**
5. Click **"Enable"**

### Step 2.3: Enable Authentication

1. Go to **Build** → **Authentication**
2. Click **"Get started"**
3. Select **"Email/Password"**
4. Enable and save

### Step 2.4: Create Storage Bucket

1. Go to **Build** → **Storage**
2. Click **"Get started"**
3. Select region: **Asia (asia-south1)**
4. Choose **"Test mode"**
5. Create bucket

### Step 2.5: Get Service Account Key

1. Go to **Project Settings** (gear icon)
2. Click **"Service Accounts"** tab
3. Click **"Generate New Private Key"**
4. Save as `firebase-config.json`
5. Place in `backend/` folder

**⚠️ IMPORTANT: Add `firebase-config.json` to `.gitignore`**

### Step 2.6: Get Web API Key

1. Go to **Project Settings** → **General**
2. Find **"Web API Key"** under "Your apps"
3. Copy the key

---

## Step 3: Backend Setup

### Step 3.1: Navigate to Backend

```bash
cd backend
```

### Step 3.2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in terminal prompt.

### Step 3.3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- Flask & Flask-CORS
- Firebase Admin SDK
- Razorpay
- QR Code & PDF libraries
- And more...

### Step 3.4: Configure Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
# or on Windows: copy .env.example .env
```

Edit `.env` file and add your values:

```env
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_PORT=5000

# Firebase Configuration
FIREBASE_PROJECT_ID=sahakar-mandal-xxxxx
FIREBASE_PRIVATE_KEY_ID=key_id_here
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@...
FIREBASE_CLIENT_ID=123456789
FIREBASE_STORAGE_BUCKET=sahakar-mandal-xxxxx.appspot.com
FIREBASE_WEB_API_KEY=AIzaSyD...    # From Step 2.6

# JWT Configuration
JWT_SECRET=your-super-secret-key-here-change-in-production

# Razorpay (Optional)
RAZORPAY_KEY_ID=rzp_test_xxxxx
RAZORPAY_KEY_SECRET=your_secret

# UPI (Optional)
UPI_ID=yourupi@upi

# URLs
API_BASE_URL=http://localhost:5000
FRONTEND_URL=http://localhost:3000
```

**How to get Firebase credentials:**

From `firebase-config.json`:
```json
{
  "project_id": "FIREBASE_PROJECT_ID",
  "private_key_id": "FIREBASE_PRIVATE_KEY_ID",
  "private_key": "FIREBASE_PRIVATE_KEY",
  "client_email": "FIREBASE_CLIENT_EMAIL",
  "client_id": "FIREBASE_CLIENT_ID",
  "type": "service_account",
  ...
}
```

### Step 3.5: Initialize Firestore with Sample Data (Optional)

```bash
python scripts/init_firestore.py
```

This creates:
- Demo users
- Sample donations
- Sample expenses
- Sample events
- Sample inventory

### Step 3.6: Start Backend Server

```bash
python app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

**✓ Backend is now running at http://localhost:5000**

---

## Step 4: Frontend Setup

### Step 4.1: Navigate to Frontend

Open **new terminal** and navigate to frontend:

```bash
cd frontend
# or from root: cd ../frontend
```

### Step 4.2: Update API URL (Optional)

Edit `frontend/js/config.js`:

```javascript
const API_BASE_URL = 'http://localhost:5000';
```

### Step 4.3: Serve Frontend Files

**Option A: Python Server (Recommended)**

```bash
python -m http.server 3000
```

Access at: http://localhost:3000

**Option B: Using VS Code Live Server**

1. Install "Live Server" extension in VS Code
2. Right-click `index.html`
3. Select "Open with Live Server"

**Option C: npm http-server**

```bash
npm install -g http-server
http-server -p 3000
```

**✓ Frontend is now running at http://localhost:3000**

---

## Step 5: Test the Application

### Access Application

Open browser and visit:

| Component | URL | Purpose |
|-----------|-----|---------|
| Landing Page | http://localhost:3000 | Home page |
| Login | http://localhost:3000/login.html | User login |
| Signup | http://localhost:3000/signup.html | New account |
| Dashboard | http://localhost:3000/dashboard.html | Main app |
| API Health | http://localhost:5000/api/health | Check API |

### Login with Demo Accounts

After running initialization script, use:

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@sahakar.com | Admin@123456 |
| Finance | finance@sahakar.com | Finance@123456 |
| Volunteer | volunteer@sahakar.com | Volunteer@123456 |

### Test Features

1. **Login**
   - Try logging in with any demo account
   - Check localStorage for token

2. **Dashboard**
   - View summary cards
   - Check charts and analytics
   - View top donors

3. **Donations**
   - Create new donation
   - View donation list
   - Filter donations

4. **Receipts**
   - Generate receipt
   - View receipt details
   - Download PDF

5. **Payments**
   - (Requires Razorpay keys for live testing)

---

## Step 6: Database Verification

### Check Firestore Data

1. Go to Firebase Console
2. Click **Firestore Database**
3. Verify collections exist:
   - users
   - donations
   - receipts
   - expenses
   - events
   - gallery
   - inventory

### Test API Endpoints

```bash
# Check API health
curl http://localhost:5000/api/health

# Get current user (requires token)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:5000/api/auth/me

# List donations
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:5000/api/donations
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'flask'"

**Solution:**
```bash
# Make sure virtual environment is activated
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# Then reinstall
pip install -r requirements.txt
```

### Issue: "Firebase config not found"

**Solution:**
1. Ensure `firebase-config.json` is in `backend/` folder
2. Check `.env` has correct `FIREBASE_CONFIG_PATH`

```bash
# Verify file exists
ls backend/firebase-config.json  # Mac/Linux
dir backend\firebase-config.json # Windows
```

### Issue: CORS errors in browser

**Solution:**
Ensure Flask is running with CORS enabled (it is by default).

### Issue: "API connection refused"

**Solution:**
1. Check backend is running (`python app.py`)
2. Check API_BASE_URL in `config.js`
3. Verify both are on same network

### Issue: Database empty after login

**Solution:**
1. Run initialization script:
   ```bash
   python scripts/init_firestore.py
   ```
2. Check Firestore collections exist
3. Verify user has correct role

### Issue: "Port already in use"

**Solution:**
```bash
# Change port in .env
FLASK_PORT=5001

# Or kill process using port
# Windows: netstat -ano | findstr :5000
# Mac/Linux: lsof -i :5000
```

---

## Project Structure

```
sahakar_mandal_project/
├── backend/
│   ├── app.py                  # Main Flask app
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example           # Environment template
│   ├── firebase-config.json   # Firebase credentials (ignored)
│   └── scripts/
│       └── init_firestore.py  # Initialize data
├── frontend/
│   ├── index.html             # Landing page
│   ├── login.html             # Login page
│   ├── signup.html            # Signup page
│   ├── dashboard.html         # Main dashboard
│   ├── receipt.html           # Receipt view
│   ├── css/
│   │   └── style.css          # Styles
│   └── js/
│       ├── config.js          # Configuration
│       ├── auth.js            # Auth logic
│       ├── dashboard.js       # Dashboard logic
│       └── ...
├── docs/
│   ├── API_DOCUMENTATION.md
│   ├── FIREBASE_SETUP.md
│   ├── DEPLOYMENT.md
│   └── MOBILE_MIGRATION.md
├── README.md
└── .gitignore
```

---

## Next Steps

After successful installation:

### 1. Configure Razorpay (Optional)

For payment processing:

```env
RAZORPAY_KEY_ID=rzp_test_xxxxx
RAZORPAY_KEY_SECRET=your_secret_here
```

### 2. Setup Firebase Rules

Go to Firestore **Rules** and add security rules from FIREBASE_SETUP.md

### 3. Test Payment Flow

Create donation → Verify payment → Check receipt

### 4. Customize Data

- Update organization name
- Add your logo/branding
- Customize colors in CSS
- Add real donor data

### 5. Prepare for Deployment

- See DEPLOYMENT.md for production setup
- Configure environment variables
- Test on staging

---

## Getting Help

### Check These Files

- **API Issues**: `docs/API_DOCUMENTATION.md`
- **Firebase Issues**: `docs/FIREBASE_SETUP.md`
- **Deployment**: `docs/DEPLOYMENT.md`
- **Mobile**: `docs/MOBILE_MIGRATION.md`

### Common Commands

```bash
# Backend
cd backend
source venv/bin/activate      # Activate virtual env
python app.py                 # Start server
python scripts/init_firestore.py  # Initialize data
deactivate                    # Deactivate virtual env

# Frontend
cd frontend
python -m http.server 3000    # Start server
# Access: http://localhost:3000
```

### Useful URLs

- **Firebase Console**: https://console.firebase.google.com
- **API Health**: http://localhost:5000/api/health
- **Frontend**: http://localhost:3000
- **Dashboard**: http://localhost:3000/dashboard.html

---

## Success Checklist

- [ ] Python 3.9+ installed
- [ ] Git installed
- [ ] Firebase project created
- [ ] Firestore database enabled
- [ ] Service account key downloaded
- [ ] firebase-config.json placed in backend/
- [ ] .env file configured
- [ ] Virtual environment created & activated
- [ ] Requirements installed
- [ ] Backend server running (port 5000)
- [ ] Frontend server running (port 3000)
- [ ] Can access http://localhost:3000
- [ ] Can login with demo account
- [ ] Dashboard shows data

---

## Support & Contact

For issues:
1. Check troubleshooting section
2. Review documentation files
3. Check console for error messages
4. Verify all configuration values

---

Last Updated: 2024
Version: 1.0.0
