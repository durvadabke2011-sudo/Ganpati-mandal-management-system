# Sahakar Mandal - Deployment Guide

Complete guide to deploy Sahakar Mandal to production.

## Table of Contents
1. Backend Deployment (Render)
2. Frontend Deployment (Netlify/Vercel)
3. Domain Setup
4. SSL Certificate
5. Environment Configuration
6. Database Migration
7. Monitoring & Maintenance

---

## Part 1: Backend Deployment (Render)

### Step 1: Prepare Repository

1. Initialize Git repository (if not done):
```bash
git init
git add .
git commit -m "Initial commit: Sahakar Mandal v1.0"
```

2. Create GitHub account and repository:
   - Go to [GitHub](https://github.com)
   - Create new repository `sahakar-mandal`
   - Push code:
```bash
git remote add origin https://github.com/yourusername/sahakar-mandal.git
git branch -M main
git push -u origin main
```

### Step 2: Create Render Account

1. Go to [Render.com](https://render.com)
2. Sign up with GitHub account
3. Give Render access to your repositories

### Step 3: Deploy Backend on Render

1. Click **"New"** → **"Web Service"**
2. Select your `sahakar-mandal` repository
3. Configure settings:
   - **Name**: `sahakar-mandal-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free (or Starter for production)

### Step 4: Set Environment Variables on Render

1. Go to Service Settings → **Environment**
2. Add all variables from `.env`:

```
FLASK_ENV=production
FLASK_DEBUG=False
FLASK_PORT=5000

FIREBASE_PROJECT_ID=your_project_id
FIREBASE_PRIVATE_KEY_ID=your_key_id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=your_email
FIREBASE_CLIENT_ID=your_id
FIREBASE_STORAGE_BUCKET=your_bucket
FIREBASE_WEB_API_KEY=your_web_key

JWT_SECRET=your_production_secret_key_here

RAZORPAY_KEY_ID=your_razorpay_key
RAZORPAY_KEY_SECRET=your_razorpay_secret

UPI_ID=yourname@upi

API_BASE_URL=https://sahakar-mandal-api.onrender.com
FRONTEND_URL=https://sahakar-mandal.netlify.app
```

### Step 5: Deploy

1. Click **"Create Web Service"**
2. Render automatically deploys on every push to `main`
3. Check deployment status in dashboard
4. Your API is now live at: `https://sahakar-mandal-api.onrender.com`

### Step 6: Verify Deployment

```bash
curl https://sahakar-mandal-api.onrender.com/api/health

# Response:
# {
#   "status": "healthy",
#   "service": "Sahakar Mandal API"
# }
```

---

## Part 2: Frontend Deployment (Netlify)

### Step 1: Prepare Frontend

Update API URL in `frontend/js/config.js`:

```javascript
const API_BASE_URL = 'https://sahakar-mandal-api.onrender.com';
```

### Step 2: Create Netlify Account

1. Go to [Netlify.com](https://netlify.com)
2. Sign up with GitHub
3. Give Netlify access to repositories

### Step 3: Deploy Frontend

#### Option A: GitHub Integration (Recommended)

1. Click **"New site from Git"**
2. Select GitHub
3. Choose `sahakar-mandal` repository
4. Configure build settings:
   - **Build Command**: Leave empty (static site)
   - **Publish Directory**: `frontend`
5. Click **"Deploy site"**

#### Option B: Drag & Drop

1. Go to Netlify
2. Drag & drop `frontend` folder
3. Site auto-deploys

### Step 4: Configure Domain

1. Go to **Site Settings** → **Domain**
2. Add custom domain (optional):
   - `sahakar-mandal.com`
3. Configure DNS with your registrar

### Step 5: Set Environment Variables

In Netlify, go to **Site Settings** → **Build & Deploy** → **Environment**:

```
VITE_API_BASE_URL=https://sahakar-mandal-api.onrender.com
VITE_APP_NAME=Sahakar Mandal
```

### Step 6: Enable HTTPS

Netlify automatically provides free SSL certificate. Check status in domain settings.

---

## Part 3: Database Migration to Production

### Step 1: Backup Existing Data

```bash
# Export Firestore data
gcloud firestore export gs://your-bucket/backup-2024-01-01
```

### Step 2: Update Firestore Rules for Production

Replace test mode rules with production rules:

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Require authentication for all operations
    function isAdmin() {
      return get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'admin';
    }
    
    function hasRole(role) {
      return get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == role;
    }
    
    // Users collection
    match /users/{userId} {
      allow read, write: if request.auth.uid == userId;
      allow read: if isAdmin();
    }
    
    // Donations
    match /donations/{document=**} {
      allow create: if request.auth != null && 
        (hasRole('admin') || hasRole('finance') || hasRole('collection'));
      allow read: if request.auth != null;
      allow update, delete: if request.auth != null && 
        (isAdmin() || hasRole('finance'));
    }
    
    // Receipts
    match /receipts/{document=**} {
      allow read: if request.auth != null;
      allow create, update: if request.auth != null && 
        (isAdmin() || hasRole('finance'));
    }
    
    // Expenses
    match /expenses/{document=**} {
      allow read, write: if request.auth != null && 
        (isAdmin() || hasRole('finance'));
    }
    
    // Events
    match /events/{document=**} {
      allow read: if true;
      allow create, update, delete: if request.auth != null && 
        (isAdmin() || hasRole('event'));
    }
    
    // Gallery
    match /gallery/{document=**} {
      allow read: if true;
      allow create, update: if request.auth != null && 
        (isAdmin() || hasRole('event'));
    }
    
    // Inventory
    match /inventory/{document=**} {
      allow read: if request.auth != null;
      allow create, update: if request.auth != null && 
        (isAdmin() || hasRole('event'));
    }
    
    // Payments
    match /payments/{document=**} {
      allow read, write: if request.auth != null && 
        (isAdmin() || hasRole('finance'));
    }
  }
}
```

### Step 3: Enable Firestore Backup

1. Go to Firestore Console
2. Click **"Backups"**
3. Set automatic daily backup
4. Retention period: 30 days

---

## Part 4: CORS Configuration

Update Flask CORS settings in `app.py`:

```python
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://sahakar-mandal.netlify.app",
            "https://sahakar-mandal.com"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})
```

---

## Part 5: SSL Certificate & HTTPS

### Render (Automatic)
- Render provides free SSL automatically
- All traffic is encrypted by default

### Custom Domain (Let's Encrypt)
1. Use Netlify's auto SSL (automatic)
2. For backend, Render handles automatically

---

## Part 6: Monitoring & Logging

### Step 1: Enable Cloud Logging (Firebase)

```bash
gcloud logging read "resource.type=cloud_firestore" --limit 50
```

### Step 2: Setup Error Tracking

Add error tracking to Flask:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

@app.errorhandler(Exception)
def handle_error(error):
    logger.error(f"Error: {str(error)}")
    return jsonify({'message': 'Internal server error'}), 500
```

### Step 3: Setup Uptime Monitoring

Use services like:
- [UptimeRobot](https://uptimerobot.com)
- [Pingdom](https://www.pingdom.com)
- [StatusPage](https://www.statuspage.io)

Configure to ping: `https://sahakar-mandal-api.onrender.com/api/health`

---

## Part 7: Performance Optimization

### Frontend Optimization

```javascript
// Lazy load images
const imageObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const img = entry.target;
      img.src = img.dataset.src;
      imageObserver.unobserve(img);
    }
  });
});

document.querySelectorAll('img[data-src]').forEach(img => {
  imageObserver.observe(img);
});
```

### Backend Optimization

```python
# Add caching
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/api/dashboard/summary')
@cache.cached(timeout=300)  # Cache for 5 minutes
def get_dashboard_summary():
    # ...
```

### Database Optimization

Create Firestore indexes:

1. Go to Firestore Console
2. **Indexes** section
3. Create composite indexes for frequent queries:
   - donations: status + date
   - events: status + date
   - expenses: category + status

---

## Part 8: Email Notifications (Optional)

### Setup SendGrid

```bash
pip install sendgrid
```

```python
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_donation_receipt(donor_email, receipt_data):
    message = Mail(
        from_email='noreply@sahakar.com',
        to_emails=donor_email,
        subject='Your Donation Receipt',
        html_content=f'<html><body>Thank you for your donation of ₹{receipt_data["amount"]}</body></html>'
    )
    
    sg = SendGridAPIClient('SENDGRID_API_KEY')
    response = sg.send(message)
    return response.status_code == 202
```

---

## Part 9: SMS Notifications (Optional)

### Setup Twilio

```bash
pip install twilio
```

```python
from twilio.rest import Client

def send_sms(phone_number, message):
    account_sid = 'YOUR_ACCOUNT_SID'
    auth_token = 'YOUR_AUTH_TOKEN'
    client = Client(account_sid, auth_token)
    
    message = client.messages.create(
        body=message,
        from_='+1234567890',
        to=f'+91{phone_number}'
    )
    
    return message.sid
```

---

## Part 10: Security Checklist

Before going live:

- [ ] HTTPS enabled on all endpoints
- [ ] Firestore rules updated for production
- [ ] API rate limiting configured
- [ ] CORS properly configured
- [ ] API keys rotated and secured
- [ ] Environment variables not exposed
- [ ] Database backups automated
- [ ] Error logging enabled
- [ ] Monitoring/alerts setup
- [ ] Security headers configured
- [ ] SQL injection prevention (N/A for Firestore)
- [ ] XSS protection enabled
- [ ] CSRF tokens implemented
- [ ] Input validation on all endpoints
- [ ] Output encoding enabled

---

## Part 11: Rollback Procedure

If deployment fails:

### Backend Rollback

1. Go to Render dashboard
2. Click "Deployments"
3. Select previous working version
4. Click "Redeploy"

### Frontend Rollback

1. Go to Netlify
2. Click "Deploys"
3. Select previous working version
4. Click "Restore"

### Database Rollback

```bash
# Restore from backup
gcloud firestore import gs://your-bucket/backup-2024-01-01
```

---

## Part 12: Scaling for Growth

### As traffic increases:

**Backend:**
- Switch from Free to Starter plan on Render
- Enable auto-scaling
- Upgrade to Performance plans

**Database:**
- Firestore auto-scales
- Monitor read/write quotas
- Optimize indexes

**Storage:**
- Monitor Firebase Storage usage
- Set up CDN for assets
- Compress images

---

## Part 13: Post-Deployment Tasks

### Day 1:
- [ ] Verify all endpoints working
- [ ] Test login/registration
- [ ] Check payment processing
- [ ] Verify email notifications
- [ ] Monitor error logs

### Week 1:
- [ ] Gather user feedback
- [ ] Monitor performance metrics
- [ ] Check analytics
- [ ] Fix any reported bugs

### Month 1:
- [ ] Review security logs
- [ ] Analyze usage patterns
- [ ] Plan features for v1.1
- [ ] Optimize based on data

---

## Production URLs

After deployment:

```
Frontend:  https://sahakar-mandal.netlify.app
Backend:   https://sahakar-mandal-api.onrender.com
Dashboard: https://sahakar-mandal.netlify.app/dashboard.html
API Docs:  https://sahakar-mandal-api.onrender.com/api/docs
```

---

## Support

For deployment issues:

- [Render Documentation](https://render.com/docs)
- [Netlify Documentation](https://docs.netlify.com)
- [Firebase Documentation](https://firebase.google.com/docs)

---

Last Updated: 2024
Version: 1.0.0
