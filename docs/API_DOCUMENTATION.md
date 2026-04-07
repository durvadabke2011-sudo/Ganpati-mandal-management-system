# Sahakar Mandal - API Documentation

## Overview

This document provides complete API reference for Sahakar Mandal backend. All endpoints require JWT authentication (except public endpoints).

### Base URL
```
http://localhost:5000/api
```

### Authentication
Include JWT token in Authorization header:
```
Authorization: Bearer <jwt_token>
```

### Response Format
All responses are in JSON format:
```json
{
  "message": "Success message",
  "data": {...},
  "timestamp": "2024-01-01T12:00:00"
}
```

### Error Handling
```json
{
  "message": "Error description",
  "status": 400,
  "error_code": "INVALID_REQUEST"
}
```

---

## Authentication Endpoints

### 1. Sign Up
Create a new user account.

**Request:**
```
POST /auth/signup
Content-Type: application/json
```

**Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePass123",
  "phone": "9876543210",
  "area": "Bandra",
  "role": "volunteer"
}
```

**Response (201):**
```json
{
  "message": "User registered successfully",
  "user_id": "uid_12345",
  "token": "eyJhbGc...",
  "role": "volunteer"
}
```

**Errors:**
- 400: Email already registered
- 400: Invalid email format
- 500: Server error

---

### 2. Login
Authenticate user and receive JWT token.

**Request:**
```
POST /auth/login
Content-Type: application/json
```

**Body:**
```json
{
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

**Response (200):**
```json
{
  "message": "Login successful",
  "user_id": "uid_12345",
  "token": "eyJhbGc...",
  "role": "volunteer",
  "name": "John Doe",
  "email": "john@example.com"
}
```

**Errors:**
- 401: Invalid email or password
- 429: Too many login attempts

---

### 3. Get Current User
Get logged-in user details.

**Request:**
```
GET /auth/me
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "user_id": "uid_12345",
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "9876543210",
  "area": "Bandra",
  "role": "volunteer",
  "status": "active",
  "created_at": "2024-01-01T10:00:00"
}
```

**Errors:**
- 401: Unauthorized
- 404: User not found

---

### 4. Logout
Logout user (clear token on frontend).

**Request:**
```
POST /auth/logout
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "message": "Logout successful"
}
```

---

## Donation Endpoints

### 1. List Donations
Get all donations with optional filters.

**Request:**
```
GET /donations?status=completed&area=Bandra&donor_name=John
Authorization: Bearer <token>
```

**Query Parameters:**
- `status`: pending, completed, failed
- `area`: Filter by area
- `donor_name`: Filter by donor name

**Response (200):**
```json
{
  "message": "Donations retrieved",
  "count": 15,
  "donations": [
    {
      "id": "donation_123",
      "donation_id": "DONATION_001",
      "donor_name": "John Doe",
      "donor_email": "john@example.com",
      "donor_mobile": "9876543210",
      "amount": 5000,
      "donation_type": "online",
      "purpose": "general",
      "area": "Bandra",
      "status": "completed",
      "date": "2024-01-01T10:00:00",
      "receipt_id": "receipt_123"
    }
  ]
}
```

---

### 2. Create Donation
Create a new donation record.

**Request:**
```
POST /donations
Authorization: Bearer <token>
Content-Type: application/json
```

**Roles Required:** admin, finance, collection

**Body:**
```json
{
  "donor_name": "Jane Doe",
  "donor_email": "jane@example.com",
  "donor_mobile": "9876543210",
  "amount": 10000,
  "donation_type": "online",
  "purpose": "education",
  "area": "Bandra",
  "building": "Tower A",
  "floor": "5",
  "flat": "501",
  "payment_method": "upi",
  "transaction_id": "TXN123456",
  "notes": "Additional notes"
}
```

**Response (201):**
```json
{
  "message": "Donation created successfully",
  "donation_id": "DONATION_002",
  "donation": {...}
}
```

---

### 3. Get Donation Details
Get specific donation details.

**Request:**
```
GET /donations/<donation_id>
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "id": "donation_123",
  "donation_id": "DONATION_001",
  "donor_name": "John Doe",
  ...
}
```

---

### 4. Update Donation
Update donation details.

**Request:**
```
PUT /donations/<donation_id>
Authorization: Bearer <token>
Content-Type: application/json
```

**Roles Required:** admin, finance, collection

**Body:**
```json
{
  "amount": 12000,
  "status": "completed",
  "notes": "Updated notes"
}
```

**Response (200):**
```json
{
  "message": "Donation updated successfully",
  "donation_id": "DONATION_001"
}
```

---

### 5. Delete Donation
Delete donation record.

**Request:**
```
DELETE /donations/<donation_id>
Authorization: Bearer <token>
```

**Roles Required:** admin, finance

**Response (200):**
```json
{
  "message": "Donation deleted successfully",
  "donation_id": "DONATION_001"
}
```

---

## Receipt Endpoints

### 1. Generate Receipt
Create receipt for a donation.

**Request:**
```
POST /receipts/<donation_id>/generate
Authorization: Bearer <token>
```

**Roles Required:** admin, finance, collection

**Response (201):**
```json
{
  "message": "Receipt generated successfully",
  "receipt_id": "RECEIPT_123",
  "receipt": {
    "receipt_id": "RECEIPT_123",
    "donation_id": "DONATION_001",
    "donor_name": "John Doe",
    "amount": 5000,
    "date": "2024-01-01",
    "status": "active"
  }
}
```

---

### 2. Get QR Code
Get QR code image for receipt.

**Request:**
```
GET /receipts/<receipt_id>/qrcode
```

**Response:**
Returns PNG image (image/png)

---

### 3. Get Receipt PDF
Download receipt as PDF.

**Request:**
```
GET /receipts/<receipt_id>/pdf
```

**Response:**
Returns PDF file (application/pdf)

---

## Payment Endpoints

### 1. Create Razorpay Order
Initiate payment order.

**Request:**
```
POST /payments/razorpay/order
Authorization: Bearer <token>
Content-Type: application/json
```

**Body:**
```json
{
  "amount": 5000,
  "donor_name": "John Doe",
  "purpose": "general"
}
```

**Response (201):**
```json
{
  "message": "Order created successfully",
  "order_id": "order_9A33XWu590gUtm",
  "amount": 5000,
  "currency": "INR"
}
```

---

### 2. Verify Payment
Verify and complete payment.

**Request:**
```
POST /payments/razorpay/verify
Authorization: Bearer <token>
Content-Type: application/json
```

**Body:**
```json
{
  "order_id": "order_9A33XWu590gUtm",
  "payment_id": "pay_9A33XWu590gUtm",
  "signature": "9ef4dffbfd84f1318f6739a3ce19f9d85851857ae648f114332d8401e0949a3d"
}
```

**Response (200):**
```json
{
  "message": "Payment verified and donation recorded",
  "donation_id": "DONATION_005",
  "payment_id": "pay_9A33XWu590gUtm"
}
```

---

### 3. Generate UPI QR Code
Generate UPI payment QR code.

**Request:**
```
POST /payments/upi/qrcode
Authorization: Bearer <token>
Content-Type: application/json
```

**Body:**
```json
{
  "amount": 5000,
  "note": "Donation"
}
```

**Response:**
Returns PNG image (image/png)

---

## Expense Endpoints

### 1. List Expenses
Get all expenses.

**Request:**
```
GET /expenses
Authorization: Bearer <token>
```

**Roles Required:** admin, finance

**Response (200):**
```json
{
  "message": "Expenses retrieved",
  "count": 10,
  "expenses": [
    {
      "id": "expense_123",
      "expense_id": "EXP_001",
      "description": "Lights and Decorations",
      "amount": 15000,
      "category": "decoration",
      "status": "approved",
      "date": "2024-01-01T10:00:00"
    }
  ]
}
```

---

### 2. Create Expense
Add new expense.

**Request:**
```
POST /expenses
Authorization: Bearer <token>
Content-Type: application/json
```

**Roles Required:** admin, finance

**Body:**
```json
{
  "description": "Prasad for event",
  "amount": 5000,
  "category": "prasad",
  "event": "Ganesh Chaturthi",
  "vendor": "Local vendor",
  "payment_method": "cash",
  "status": "approved",
  "notes": "Distribution materials"
}
```

**Response (201):**
```json
{
  "message": "Expense created successfully",
  "expense_id": "EXP_002"
}
```

---

## Dashboard Endpoints

### 1. Get Summary
Get financial summary.

**Request:**
```
GET /dashboard/summary
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "total_donations": 500000,
  "total_expenses": 100000,
  "balance": 400000,
  "donation_count": 150,
  "timestamp": "2024-01-01T10:00:00"
}
```

---

### 2. Get Yearly Data
Get year-wise donation data.

**Request:**
```
GET /dashboard/donations-yearly?year=2024
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "year": "2024",
  "monthly_data": {
    "1": 50000,
    "2": 60000,
    "3": 45000,
    ...
    "12": 40000
  }
}
```

---

### 3. Get Top Donors
Get leaderboard of top donors.

**Request:**
```
GET /dashboard/top-donors?limit=10
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "leaderboard": [
    {
      "rank": 1,
      "name": "John Doe",
      "total_amount": 150000,
      "donation_count": 25
    },
    {
      "rank": 2,
      "name": "Jane Smith",
      "total_amount": 120000,
      "donation_count": 20
    }
  ]
}
```

---

## Event Endpoints

### 1. List Events
Get all events.

**Request:**
```
GET /events
```

**Response (200):**
```json
{
  "message": "Events retrieved",
  "count": 5,
  "events": [
    {
      "id": "event_123",
      "event_id": "EVENT_001",
      "title": "Ganesh Chaturthi",
      "description": "Annual celebration",
      "date": "2024-09-07",
      "location": "Community Center",
      "status": "scheduled",
      "budget": 100000
    }
  ]
}
```

---

### 2. Create Event
Create new event.

**Request:**
```
POST /events
Authorization: Bearer <token>
Content-Type: application/json
```

**Roles Required:** admin, event

**Body:**
```json
{
  "title": "Diwali Celebration",
  "description": "Grand Diwali event",
  "date": "2024-11-01",
  "start_time": "18:00",
  "end_time": "22:00",
  "location": "Community Park",
  "category": "festival",
  "budget": 150000,
  "notes": "All preparations done"
}
```

**Response (201):**
```json
{
  "message": "Event created successfully",
  "event_id": "EVENT_002"
}
```

---

## Gallery Endpoints

### 1. List Gallery
Get gallery images.

**Request:**
```
GET /gallery?event=EVENT_001
```

**Response (200):**
```json
{
  "message": "Gallery retrieved",
  "count": 20,
  "gallery": [
    {
      "id": "gallery_123",
      "gallery_id": "GAL_001",
      "title": "Event Opening",
      "event_id": "EVENT_001",
      "url": "https://storage.firebase.com/...",
      "created_at": "2024-01-01T10:00:00"
    }
  ]
}
```

---

### 2. Upload Image
Upload gallery image.

**Request:**
```
POST /gallery
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Form Data:**
- `file`: Image file (PNG, JPG, etc.)
- `event_id`: Associated event ID
- `title`: Image title
- `description`: Image description

**Response (201):**
```json
{
  "message": "Gallery item uploaded successfully",
  "gallery_id": "GAL_002",
  "url": "https://storage.firebase.com/..."
}
```

---

## User Management Endpoints (Admin Only)

### 1. List Users
Get all users.

**Request:**
```
GET /users
Authorization: Bearer <token>
```

**Roles Required:** admin

**Response (200):**
```json
{
  "message": "Users retrieved",
  "count": 50,
  "users": [...]
}
```

---

### 2. Update User Role
Change user role.

**Request:**
```
PUT /users/<user_id>/role
Authorization: Bearer <token>
Content-Type: application/json
```

**Roles Required:** admin

**Body:**
```json
{
  "role": "finance"
}
```

**Response (200):**
```json
{
  "message": "User role updated successfully",
  "user_id": "uid_12345",
  "role": "finance"
}
```

---

## Inventory Endpoints

### 1. List Inventory
Get inventory items.

**Request:**
```
GET /inventory
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "message": "Inventory retrieved",
  "count": 30,
  "items": [
    {
      "id": "item_123",
      "name": "Stage Lights",
      "quantity": 10,
      "category": "equipment",
      "condition": "good"
    }
  ]
}
```

---

### 2. Create Inventory Item
Add new inventory item.

**Request:**
```
POST /inventory
Authorization: Bearer <token>
Content-Type: application/json
```

**Roles Required:** admin, event

**Body:**
```json
{
  "name": "Microphone",
  "description": "Wireless microphone",
  "category": "equipment",
  "quantity": 5,
  "unit": "piece",
  "condition": "good",
  "location": "Main Hall",
  "purchase_date": "2023-01-01",
  "cost": 5000
}
```

**Response (201):**
```json
{
  "message": "Inventory item created successfully",
  "item_id": "ITEM_050"
}
```

---

## Error Codes

| Code | Message | HTTP Status |
|------|---------|-------------|
| INVALID_REQUEST | Invalid request parameters | 400 |
| UNAUTHORIZED | Missing or invalid token | 401 |
| FORBIDDEN | Insufficient permissions | 403 |
| NOT_FOUND | Resource not found | 404 |
| CONFLICT | Resource already exists | 409 |
| RATE_LIMITED | Too many requests | 429 |
| SERVER_ERROR | Internal server error | 500 |

---

## Rate Limiting

- **Default**: 200 requests/day, 50 requests/hour per IP
- **Auth Endpoints**: 5 requests/minute
- **Payment Endpoints**: 10 requests/minute

---

## WebSocket Events (Future)

- `notification:donation` - New donation received
- `notification:event` - Event update
- `notification:expense` - Expense update
- `status:payment` - Payment status change

---

## Migration Guide for Mobile Apps

This API is mobile-app ready. Key points:

1. **Token-Based Auth**: Use JWT tokens for mobile auth
2. **JSON Responses**: All responses are JSON
3. **Multipart Uploads**: Use form-data for file uploads
4. **CORS Enabled**: Mobile apps can make cross-origin requests
5. **RESTful Design**: Standard HTTP methods (GET, POST, PUT, DELETE)

---

## API Versioning

Current Version: **v1**

Future versions will be backwards compatible.

---

Last Updated: 2024
Version: 1.0.0
