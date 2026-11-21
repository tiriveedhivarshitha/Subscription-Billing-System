Subscription Billing Automation System

A full-stack subscription billing and plan management platform built with FastAPI and Oracle XE. The system automates the complete subscription lifecycle — from plan creation and payment processing to invoice generation and subscription expiry — with separate portals for Admins and Customers.

🚀 Features
👨‍💼 Admin Portal
Plan Management — Create, edit, archive, and restore subscription plans with custom features and pricing
Customer Overview — View all registered customers
Failed Payments — Monitor and track failed payment transactions
Audit Logs — Complete activity log of every action performed in the system
Power BI Analytics Dashboard — Embedded live reports for:
Business Overview (revenue, subscriptions)
Plan Analytics (most purchased plans, revenue per plan)
Customer Analytics (customer behavior and trends)
Payment Analytics (payment methods, failed payments breakdown)
👤 Customer Portal
Explore Plans — Browse all active plans with features, pricing, and GST breakdown; search plans by name
Subscribe — Select a payment method (UPI, Credit Card, Debit Card, Net Banking) and subscribe with mock payment processing
Free Trial — Take a free trial for eligible plans (trial period auto-managed)
My Invoices — View all invoices, filter by Invoice ID, and download PDF invoices
My Subscriptions — View all active and trial subscriptions with days remaining
Notifications — Automatic alerts for subscriptions expiring within 7 days with one-click renewal
My Profile — View account details (Customer ID, Email) and activity summary (active plans, total invoices, total spent)
⚙️ System Features
JWT Role-Based Authentication — Separate access control for Admin and Customer roles
Mock Payment Gateway — Simulates real payment processing with 80% success rate
Auto PDF Invoice Generation — PDF invoices generated automatically on successful payment
Automated Subscription Lifecycle — Background scheduler auto-expires subscriptions at end date
18% GST Calculation — Tax automatically calculated and shown in payment breakdown and invoices
🛠️ Tech Stack
Layer	Technology
Backend	Python, FastAPI
Database	Oracle XE (oracledb)
Authentication	JWT (PyJWT)
Frontend	HTML, CSS, JavaScript (Vanilla)
Analytics	Microsoft Power BI Embedded
PDF Generation	ReportLab
Background Tasks	APScheduler
Environment Config	python-dotenv
📁 Project Structure
subscription-billing-system/
│
├── Backend/
│   ├── main.py                      # FastAPI app entry point
│   ├── pydanticModel.py             # Request/response data models
│   ├── dependencies.py              # JWT auth dependency
│   ├── .env                         # Environment variables (not committed)
│   ├── routes/
│   │   ├── auth.py                  # Signup & Signin routes
│   │   ├── admin.py                 # Admin portal routes
│   │   └── customer.py              # Customer portal routes
│   └── database/
│       └── oracleDBconnection.py    # Oracle DB connection
│
└── frontend/
    ├── index.html                   # Login page
    ├── signup.html                  # Signup page
    ├── style.css                    # Login/signup styles
    ├── script.js                    # Auth logic (login/signup)
    ├── admin-dashboard.html         # Admin portal UI
    ├── admin-dashboard.js           # Admin portal logic
    ├── customer-dashboard.html      # Customer portal UI
    └── customer-dashboard.js        # Customer portal logic

The Admin dashboard embeds four live Power BI report pages:

Overview — Total revenue, active customers, subscription trends
Plan Analytics — Most purchased plans, revenue per plan, active subscriptions per plan
Customer Analytics — Customer acquisition and plan preference insights
Payments — Payment method distribution, failed payment analysis
