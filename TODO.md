# Pending Tasks

## Completed Tasks

### Dual Database Configuration - COMPLETED ✅
- [x] ~~Updated .env file with both database configurations~~ - COMPLETED
- [x] ~~Added AJO_DB_* environment variables for ajo-platform-db~~ - COMPLETED
- [x] ~~Enhanced BaseConfig with Ajo database properties~~ - COMPLETED
- [x] ~~Created get_ajo_db_connection() function~~ - COMPLETED
- [x] ~~Tested both database connections~~ - COMPLETED
- [x] ~~Updated test_task11.py to use AJO configuration variables~~ - COMPLETED
- [x] ~~Verified all scripts point to correct database variables~~ - COMPLETED

**Configuration:**
- **CWB Database (cwb-database)**: For finhealth functionality - use `get_db_connection()`
- **Ajo Database (ajo-platform-db)**: For Ajo functionality - use `get_ajo_db_connection()`
- Both databases use same credentials but different database names
- Environment variables loaded from root `.env` file

**Scripts verified:**
- `test_task11.py`: Updated to use AJO_DB_* variables ✅
- `functions/database.py`: Provides both connection functions ✅
- Existing finhealth functions: Continue using `get_db_connection()` ✅
- Future Ajo functions: Will use `get_ajo_db_connection()` ✅

### Task 11: Design Ajo-Specific Database Schema - COMPLETED ✅
- [x] ~~Create `database/migrations/` directory~~ - COMPLETED (already existed)
- [x] ~~Design `ajo_groups` table schema~~ - COMPLETED (already existed)
- [x] ~~Design `group_members` table schema~~ - COMPLETED (already existed)
- [x] ~~Design `contributions` table schema~~ - COMPLETED (already existed)
- [x] ~~Design `payments` table schema~~ - COMPLETED (created 004_create_payments_table.sql)
- [x] ~~Create migration script for new tables~~ - COMPLETED (004_create_payments_table.sql)
- [x] ~~Test migration script on clean database~~ - COMPLETED (test_task11.py passes all tests)

**Database:** `ajo-platform-db` contains all required tables:
- `ajo_groups` - Group management with contribution amounts, frequency, members limit
- `group_members` - Membership tracking with roles and payment positions
- `contributions` - Member contribution tracking with payment status
- `payments` - External payment processor integration (Stripe, PayPal, bank transfers)
- `distributions` - Fund distribution to receiving members
- `users` - User accounts and profiles

**Features implemented:**
- Comprehensive foreign key relationships
- Business logic constraints (positive amounts, valid statuses)
- Performance indexes for common queries
- Audit trails with created_at/updated_at timestamps
- Payment provider integration ready for Tasks 36-45

### Task 28: Group Discovery Interface - Performance Optimization
**🚀 RECOMMENDED IMMEDIATE FIX: Fast Modal with Progressive Enhancement**

**Current Issue:**
- Modal loading delay of ~500ms due to multiple sequential database calls:
  1. User ID lookup from email (`SELECT id FROM users WHERE email = %s`)
  2. Group membership check (`SELECT id FROM group_members WHERE...`)
  3. Group details with aggregation (`SELECT ... COUNT(gm.id) ... GROUP BY ...`)
  4. Member details fetch (`SELECT gm.role, gm.payment_position, u.full_name...`)
  5. Join eligibility check (`can_user_join_group` - 2-3 additional queries)

**Optimization Strategy: "Fast Modal with Progressive Enhancement"**
- ✅ Store user ID in session (eliminate user lookup)
- ✅ Use existing group data for immediate modal display
- ✅ Fetch only member details asynchronously
- ✅ Show loading spinner for member section only

**Expected Impact:**
- 🎯 Reduce delay from ~500ms to ~50ms (90% improvement)
- 🎯 Maintain all functionality
- 🎯 Require minimal code changes
- 🎯 Improve user experience significantly

**Implementation Priority:** HIGH - Quick win with major UX impact

## Technical Debt from Task Implementation

### Task 2: Enhanced Password Security - Technical Debt
- [x] ~~Add browser interface for registration~~ - COMPLETED
- [x] ~~Add password confirmation field~~ - COMPLETED  
- [x] ~~Add mode switching between login/register~~ - COMPLETED
- [ ] Replace hardcoded timestamp in `register_user()` with actual datetime
- [ ] Move from in-memory USERS_DB to proper database storage
- [ ] Add email format validation to registration process
- [ ] Consider adding password history to prevent reuse
- [ ] Add password strength meter to UI for better user experience
- [ ] Add form validation feedback in real-time (before submission)

### Group Creation Error Handling - Technical Debt
**Issue:** Misleading error messages mask database connectivity problems
- **Problem**: When internet/database connection fails during group creation, the system shows "User with email {email} not found" instead of indicating a connection problem
- **Root Cause**: `get_user_id_by_email()` in `services/group_service.py` returns `None` for both "user not found" and "database connection failed" scenarios
- **Impact**: Users think their account doesn't exist when the real issue is network connectivity
- **Discovery**: Found during group creation testing when internet was disconnected
- **Current Behavior**: `create_group()` always interprets `None` result as "user not found"
- **Expected Behavior**: Should distinguish between:
  - "Unable to access user database. Please check your internet connection."
  - "User account not found. Please ensure you're logged in correctly."
  - "Database error occurred. Please try again later."
- **Files Affected**: `services/group_service.py` lines 127-150 (get_user_id_by_email) and lines 175-180 (create_group)
- **Priority**: MEDIUM - Affects user experience during network issues

## Security Improvements

### Database Connection Security
- [ ] Remove hardcoded fallback credentials from `functions/database.py:get_db_connection()`
- [ ] Add environment variable validation to ensure all required DB credentials are provided
- [ ] Add `.env` files to `.gitignore` to prevent credential exposure
- [ ] Rotate database credentials that were previously committed to version control
- [ ] Consider implementing connection pooling for better resource management

### Environment Variables
- [ ] Move `cwb-db.env` to project root as `.env`
- [ ] Create `.env.example` template file for new developers
- [ ] Document environment variable requirements in README.md

## Code Improvements
- [ ] Add error handling for missing environment variables
- [ ] Add logging instead of print statements for database operations
- [ ] Add connection timeout configuration
- [ ] Consider implementing connection retry logic

## Machine Learning Improvements

### Model Evaluation and Metrics
- [ ] Implement confidence interval calculations for forecasts
- [ ] Add cross-validation for more robust performance estimates
- [ ] Implement rolling-window evaluation for time series
- [ ] Add error analysis by time horizon (7d, 14d, 30d patterns)
- [ ] Add seasonality impact analysis on forecast accuracy
- [ ] Implement anomaly detection in forecast errors
- [ ] Add evaluation of prediction intervals coverage

### Experiment Tracking
- [ ] Set up structured experiment logging with MLflow or Weights & Biases
- [ ] Add automated hyperparameter logging
- [ ] Implement experiment comparison visualization
- [ ] Add model performance tracking over time
- [ ] Create automated experiment reports
- [ ] Add A/B testing framework for model comparison

### Metric Improvements
- [ ] Add domain-specific financial metrics (e.g., Value at Risk)
- [ ] Implement custom loss functions for financial forecasting
- [ ] Add robustness metrics for extreme events
- [ ] Implement feature importance tracking over time
- [ ] Add model calibration metrics
- [ ] Implement baseline model comparisons

### Technical Debt
- [ ] Refactor metric calculation for better modularity
- [ ] Add type hints to evaluation functions
- [ ] Improve error handling in hyperparameter parsing
- [ ] Add validation for experiment configuration files
- [ ] Create unified evaluation pipeline
- [ ] Add automated metric threshold checking

### Assessment and Decision Logic
- [ ] Add configurable thresholds for confidence levels
- [ ] Implement risk-adjusted affordability scoring
- [ ] Add historical assessment accuracy tracking
- [ ] Implement multi-factor assessment criteria
- [ ] Add automated threshold optimization
- [ ] Implement assessment confidence scoring
- [ ] Add assessment decision explanations

### Reporting Improvements
- [ ] Add visualization of assessment results
- [ ] Implement PDF report generation
- [ ] Add historical assessment comparisons
- [ ] Implement assessment audit trail
- [ ] Add automated assessment notifications
- [ ] Create assessment summary dashboard

## Documentation
- [ ] Add setup instructions for new developers
- [ ] Document database schema and relationships
- [ ] Add API documentation for database functions
- [ ] Document machine learning model architecture and parameters
- [ ] Add documentation for feature engineering process
- [ ] Document model training and evaluation procedures
- [ ] Add example notebooks for model usage
- [ ] Document evaluation metrics and their interpretation
- [ ] Add troubleshooting guide for common evaluation issues
- [ ] Create model performance reporting templates
- [ ] Document assessment criteria and thresholds
- [ ] Add assessment result interpretation guide
- [ ] Create assessment report templates 