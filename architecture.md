# Ajo Community Savings Platform - Architecture Documentation

## Overview

The Ajo platform is a community-based savings application built with **Dash** (Python web framework) that enables groups of 5-10 people to contribute fixed amounts (£50, £100, £500, £800) on a regular basis (weekly/monthly). The pooled contributions are distributed to one member at a time over the duration of the scheme.

## Current Architecture Review

### Technology Stack

**Frontend Framework:**
- **Dash** (v2.18.2) - Python-based web framework for interactive applications
- **Dash Bootstrap Components** (v1.7.1) - UI components library
- **Plotly** (v6.0.0) - Data visualization library

**Backend:**
- **Flask** (v3.0.3) - Underlying web server (via Dash)
- **Python** - Primary programming language
- **Werkzeug** (v3.0.6) - Password hashing and security utilities

**Database:**
- **PostgreSQL** - Primary database system
- **psycopg2-binary** (v2.9.10) - PostgreSQL adapter for Python

**Deployment:**
- **Google Cloud Platform** - Hosting platform
- **Gunicorn** (v21.2.0) - WSGI HTTP server
- **Cloud Build** - CI/CD pipeline configuration

**Additional Libraries:**
- **pandas** (v2.2.3) - Data manipulation and analysis
- **numpy** (v2.2.3) - Numerical computing
- **python-dotenv** (v1.1.0) - Environment variable management

### Current File Structure Analysis

```
cwb-portal-ajo/
├── app.py                    # Main application entry point & authentication logic
├── auth.py                   # User authentication functions
├── callbacks.py              # Global callback definitions
├── requirements.txt          # Python dependencies
├── TODO.md                   # Development roadmap
├── README.md                 # Project documentation
├── cloudbuild.yaml          # GCP deployment configuration
├── app.yaml                 # GCP App Engine configuration
├── .gcloudignore            # GCP deployment exclusions
├── .gitignore               # Git exclusions
├── __init__.py              # Package initialization
│
├── pages/                   # Multi-page application structure
│   ├── home.py              # Dashboard/landing page
│   ├── groups.py            # Ajo groups management
│   ├── payments.py          # Payment tracking and history
│   ├── profile.py           # User profile management
│   ├── support.py           # Customer support and FAQ
│   ├── finhealth.py         # Financial health assessment
│   └── affordability.py     # Affordability analysis
│
├── components/              # Reusable UI components
│   ├── login.py             # Authentication interface
│   ├── navbar.py            # Navigation bar
│   ├── footer.py            # Page footer
│   ├── dashboard_cards.py   # Dashboard statistics cards
│   ├── groups.py            # Group listing and management components
│   ├── activity.py          # Activity feed components
│   ├── modals.py            # Modal dialog components
│   └── graph.py             # Data visualization components
│
├── functions/               # Business logic and utilities
│   ├── database.py          # Database connection and operations
│   ├── machinelearning.py   # ML models for credit assessment
│   ├── ml_evaluation.py     # ML model evaluation utilities
│   ├── applicant_assessment_results.py # Assessment result processing
│   └── cwb-db.env          # Database configuration
│
├── assets/                  # Static files (CSS, images, JS)
├── archive/                 # Archived/deprecated files
├── venv/                    # Virtual environment
└── __pycache__/            # Python bytecode cache
```

### Current Architecture Components

#### 1. **Application Layer** (`app.py`)
- **Dash application initialization** with multi-page support
- **Session management** using Dash stores
- **Authentication routing** - redirects unauthenticated users to login
- **Global layout structure** with header and page container
- **Color scheme definition** for consistent UI theming

#### 2. **Authentication System** (`auth.py`)
- **Mock user database** with hashed passwords (Werkzeug)
- **Session timeout management** (currently 30 minutes)
- **User validation functions**
- **Basic security** with password hashing

#### 3. **Page Management** (`pages/`)
- **Multi-page architecture** using Dash's page registration system
- **Individual page modules** for different functionalities:
  - **Home** - Dashboard with user overview
  - **Groups** - Ajo group management
  - **Payments** - Transaction history and management
  - **Profile** - User account settings
  - **Support** - Help and customer service
  - **Financial Health** - Credit assessment tools
  - **Affordability** - Financial capability analysis

#### 4. **UI Components** (`components/`)
- **Modular component design** for reusability
- **Bootstrap-based styling** for responsive design
- **Interactive elements** (modals, cards, navigation)
- **Data visualization components** using Plotly

#### 5. **Business Logic** (`functions/`)
- **Database operations** with PostgreSQL connection management
- **Machine learning integration** for credit assessment
- **Data processing utilities** using pandas/numpy
- **Security considerations** (TODO: improve credential management)

#### 6. **State Management**
- **Client-side state** via Dash stores (`dcc.Store`)
- **Session data** stored in browser memory
- **Database persistence** for long-term data storage
- **Callback-driven interactions** between components

### Current Data Flow

1. **User Authentication:**
   ```
   User Login → auth.py validation → Session store → Page routing
   ```

2. **Page Navigation:**
   ```
   URL change → app.py routing → Page component → UI rendering
   ```

3. **Database Operations:**
   ```
   User interaction → Callback trigger → functions/database.py → PostgreSQL
   ```

4. **Component Communication:**
   ```
   User action → Dash callback → State update → Component re-render
   ```

## Recommended Future Architecture

### Core Ajo Platform Requirements

Based on the Ajo concept, the platform needs to support:

1. **Group Management**
   - Create/join Ajo groups (5-10 members)
   - Set contribution amounts (£50, £100, £500, £800)
   - Define payment schedules (weekly/monthly)
   - Manage group membership and roles

2. **Payment Processing**
   - Automated payment collection
   - Payment verification and tracking
   - Distribution management
   - Payment reminders and notifications

3. **Financial Transparency**
   - Real-time balance tracking
   - Payment history and receipts
   - Group financial statements
   - Audit trails

4. **User Management**
   - Identity verification
   - Credit scoring integration
   - Communication system
   - Dispute resolution

### Recommended Architecture Evolution

#### 1. **Enhanced Backend Architecture**

```
Microservices-Based Backend:
├── User Service               # Authentication, profiles, KYC
├── Group Service             # Ajo group management
├── Payment Service           # Payment processing & tracking
├── Notification Service      # Email, SMS, push notifications
├── Credit Assessment Service # ML-based credit scoring
├── Audit Service            # Financial audit and compliance
└── API Gateway              # Request routing and authentication
```

#### 2. **Database Architecture Enhancement**

**Current:** Single PostgreSQL database
**Recommended:** Multi-database approach

```sql
-- User Management Database
Users
UserProfiles
UserDocuments
CreditScores

-- Group Management Database
AjoGroups
GroupMembers
GroupSettings
GroupSchedules

-- Financial Database
Contributions
Payments
Distributions
FinancialStatements
AuditLogs

-- Communication Database
Messages
Notifications
DisputeResolutions
```

#### 3. **Frontend Architecture Improvements**

**Current State Management:**
- Dash stores (client-side)
- Session-based authentication

**Recommended Enhancements:**
```python
# Centralized State Management
├── stores/
│   ├── user_store.py         # User session and profile data
│   ├── group_store.py        # Group membership and settings
│   ├── payment_store.py      # Payment status and history
│   └── notification_store.py # Real-time notifications

# Enhanced Component Architecture
├── components/
│   ├── auth/                 # Authentication components
│   ├── groups/               # Group management components
│   ├── payments/             # Payment-related components
│   ├── dashboard/            # Dashboard widgets
│   ├── notifications/        # Notification components
│   └── shared/               # Common UI components
```

#### 4. **Security Enhancements**

**Current Issues:**
- Hardcoded database credentials
- Basic session management
- Limited input validation

**Recommended Security Layer:**
```python
# Enhanced Security Architecture
├── security/
│   ├── authentication.py     # JWT-based authentication
│   ├── authorization.py      # Role-based access control
│   ├── encryption.py         # Data encryption utilities
│   ├── validation.py         # Input validation and sanitization
│   └── audit.py             # Security audit logging

# Environment Management
├── config/
│   ├── development.py        # Development configuration
│   ├── staging.py           # Staging environment config
│   ├── production.py        # Production environment config
│   └── secrets.py           # Secret management (Azure Key Vault/AWS Secrets)
```

#### 5. **Payment Integration Architecture**

```python
# Payment Processing Layer
├── payments/
│   ├── processors/
│   │   ├── stripe_processor.py    # Stripe integration
│   │   ├── paypal_processor.py    # PayPal integration
│   │   └── bank_transfer.py       # Direct bank transfers
│   ├── validators/
│   │   ├── payment_validator.py   # Payment verification
│   │   └── fraud_detection.py     # Fraud prevention
│   └── schedulers/
│       ├── contribution_scheduler.py # Automated contributions
│       └── distribution_scheduler.py # Automated distributions
```

#### 6. **Real-time Communication**

```python
# Real-time Features
├── realtime/
│   ├── websocket_handler.py       # WebSocket connections
│   ├── notification_service.py    # Push notifications
│   ├── chat_service.py           # Group messaging
│   └── live_updates.py           # Real-time balance updates
```

### Deployment Architecture Recommendations

#### Current Deployment
- Google Cloud Platform
- Single App Engine instance
- Single PostgreSQL database

#### Recommended Deployment Evolution

```yaml
# Kubernetes-based Deployment
Production Environment:
├── Frontend Cluster
│   ├── Dash Application (3 replicas)
│   ├── Load Balancer
│   └── CDN for static assets
├── Backend Services Cluster
│   ├── User Service (2 replicas)
│   ├── Group Service (2 replicas)
│   ├── Payment Service (3 replicas) # Critical service
│   └── Notification Service (2 replicas)
├── Database Cluster
│   ├── Primary PostgreSQL (Write)
│   ├── Read Replicas (2 instances)
│   └── Redis Cache
└── Monitoring & Logging
    ├── Application Performance Monitoring
    ├── Error Tracking
    └── Audit Log Management
```

### Migration Strategy

#### Phase 1: Foundation (Immediate - 2-4 weeks)
1. **Security Hardening**
   - Remove hardcoded credentials
   - Implement proper environment management
   - Add input validation and sanitization
   - Enhance authentication system

2. **Database Enhancement**
   - Design proper Ajo-specific database schema
   - Implement data migration scripts
   - Add proper indexing and constraints

#### Phase 2: Core Ajo Features (4-8 weeks)
1. **Group Management System**
   - Complete group creation and management
   - Member invitation and approval system
   - Payment schedule configuration

2. **Payment Integration**
   - Integrate payment processor (Stripe/PayPal)
   - Implement automated payment collection
   - Build payment verification system

#### Phase 3: Advanced Features (8-12 weeks)
1. **Real-time Features**
   - WebSocket integration for live updates
   - Push notification system
   - Group messaging system

2. **Financial Tools**
   - Enhanced credit assessment
   - Financial health monitoring
   - Automated reporting and audit trails

#### Phase 4: Scale & Optimize (12+ weeks)
1. **Microservices Migration**
   - Break down monolithic structure
   - Implement API gateway
   - Container-based deployment

2. **Advanced Analytics**
   - Business intelligence dashboard
   - Predictive analytics for default risk
   - Performance optimization

### Development Best Practices

1. **Code Organization**
   - Follow SOLID principles
   - Implement dependency injection
   - Use type hints throughout codebase
   - Comprehensive unit and integration testing

2. **API Design**
   - RESTful API design principles
   - Comprehensive API documentation
   - Version management strategy
   - Rate limiting and throttling

3. **Data Management**
   - Database migrations with version control
   - Data backup and recovery procedures
   - GDPR compliance for user data
   - Regular security audits

4. **Monitoring & Observability**
   - Application performance monitoring
   - Error tracking and alerting
   - Business metrics dashboard
   - User behavior analytics

This architecture provides a solid foundation for building a robust, scalable Ajo community savings platform while maintaining the current development momentum and allowing for incremental improvements. 