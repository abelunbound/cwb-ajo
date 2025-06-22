-- Task 17: Add Financial Summary Views
-- Migration: 006_create_financial_summary_views.sql
-- Creates database views for convenient financial reporting

-- 1. Group Financial Summary View
-- Provides comprehensive financial overview for each group
CREATE OR REPLACE VIEW group_financial_summary AS
SELECT 
    ag.id as group_id,
    ag.name as group_name,
    ag.contribution_amount,
    ag.frequency,
    ag.start_date,
    ag.duration_months,
    ag.max_members,
    ag.status as group_status,
    
    -- Member statistics
    COUNT(DISTINCT gm.user_id) as total_members,
    COUNT(DISTINCT CASE WHEN gm.status = 'active' THEN gm.user_id END) as active_members,
    
    -- Contribution statistics
    COUNT(c.id) as total_contributions,
    COUNT(CASE WHEN c.status = 'paid' THEN c.id END) as paid_contributions,
    COUNT(CASE WHEN c.status = 'pending' THEN c.id END) as pending_contributions,
    COUNT(CASE WHEN c.status = 'overdue' THEN c.id END) as overdue_contributions,
    
    -- Financial totals
    COALESCE(SUM(CASE WHEN c.status = 'paid' THEN c.amount ELSE 0 END), 0) as total_collected,
    COALESCE(SUM(CASE WHEN c.status = 'pending' THEN c.amount ELSE 0 END), 0) as total_pending,
    COALESCE(SUM(CASE WHEN c.status = 'overdue' THEN c.amount ELSE 0 END), 0) as total_overdue,
    
    -- Distribution statistics
    COUNT(d.id) as total_distributions,
    COUNT(CASE WHEN d.status = 'completed' THEN d.id END) as completed_distributions,
    COUNT(CASE WHEN d.status = 'pending' THEN d.id END) as pending_distributions,
    COALESCE(SUM(CASE WHEN d.status = 'completed' THEN d.amount ELSE 0 END), 0) as total_distributed,
    
    -- Calculated metrics
    CASE 
        WHEN COUNT(DISTINCT CASE WHEN gm.status = 'active' THEN gm.user_id END) > 0 
        THEN ROUND(
            COUNT(CASE WHEN c.status = 'paid' THEN c.id END)::numeric / 
            COUNT(DISTINCT CASE WHEN gm.status = 'active' THEN gm.user_id END)::numeric * 100, 2
        )
        ELSE 0 
    END as contribution_rate_percent,
    
    ag.contribution_amount * COUNT(DISTINCT CASE WHEN gm.status = 'active' THEN gm.user_id END) as expected_monthly_total,
    
    -- Timestamps
    ag.created_at,
    MAX(c.created_at) as last_contribution_date,
    MAX(d.created_at) as last_distribution_date

FROM ajo_groups ag
LEFT JOIN group_members gm ON ag.id = gm.group_id
LEFT JOIN contributions c ON ag.id = c.group_id
LEFT JOIN distributions d ON ag.id = d.group_id
GROUP BY ag.id, ag.name, ag.contribution_amount, ag.frequency, ag.start_date, 
         ag.duration_months, ag.max_members, ag.status, ag.created_at;

-- 2. Member Contribution Summary View
-- Tracks individual member contribution performance across all groups
CREATE OR REPLACE VIEW member_contribution_summary AS
SELECT 
    u.id as user_id,
    u.full_name,
    u.email,
    
    -- Group membership statistics
    COUNT(DISTINCT gm.group_id) as total_groups,
    COUNT(DISTINCT CASE WHEN gm.status = 'active' THEN gm.group_id END) as active_groups,
    COUNT(DISTINCT CASE WHEN gm.role = 'admin' THEN gm.group_id END) as admin_groups,
    
    -- Contribution statistics
    COUNT(c.id) as total_contributions,
    COUNT(CASE WHEN c.status = 'paid' THEN c.id END) as paid_contributions,
    COUNT(CASE WHEN c.status = 'pending' THEN c.id END) as pending_contributions,
    COUNT(CASE WHEN c.status = 'overdue' THEN c.id END) as overdue_contributions,
    COUNT(CASE WHEN c.status = 'cancelled' THEN c.id END) as cancelled_contributions,
    
    -- Financial totals
    COALESCE(SUM(CASE WHEN c.status = 'paid' THEN c.amount ELSE 0 END), 0) as total_contributed,
    COALESCE(SUM(CASE WHEN c.status = 'pending' THEN c.amount ELSE 0 END), 0) as total_pending,
    COALESCE(SUM(CASE WHEN c.status = 'overdue' THEN c.amount ELSE 0 END), 0) as total_overdue,
    
    -- Distribution statistics
    COUNT(d.id) as total_distributions_received,
    COUNT(CASE WHEN d.status = 'completed' THEN d.id END) as completed_distributions_received,
    COALESCE(SUM(CASE WHEN d.status = 'completed' THEN d.amount ELSE 0 END), 0) as total_received,
    
    -- Performance metrics
    CASE 
        WHEN COUNT(c.id) > 0 
        THEN ROUND(COUNT(CASE WHEN c.status = 'paid' THEN c.id END)::numeric / COUNT(c.id)::numeric * 100, 2)
        ELSE 0 
    END as payment_rate_percent,
    
    CASE 
        WHEN COUNT(c.id) > 0 
        THEN ROUND(COUNT(CASE WHEN c.status = 'overdue' THEN c.id END)::numeric / COUNT(c.id)::numeric * 100, 2)
        ELSE 0 
    END as overdue_rate_percent,
    
    -- Net position (received - contributed)
    COALESCE(SUM(CASE WHEN d.status = 'completed' THEN d.amount ELSE 0 END), 0) - 
    COALESCE(SUM(CASE WHEN c.status = 'paid' THEN c.amount ELSE 0 END), 0) as net_position,
    
    -- Recent activity
    MAX(c.created_at) as last_contribution_date,
    MAX(c.paid_date) as last_payment_date,
    MAX(d.distribution_date) as last_distribution_date,
    
    -- User details
    u.verification_status,
    u.created_at as user_created_at

FROM users u
LEFT JOIN group_members gm ON u.id = gm.user_id
LEFT JOIN contributions c ON u.id = c.user_id
LEFT JOIN distributions d ON u.id = d.recipient_id
GROUP BY u.id, u.full_name, u.email, u.verification_status, u.created_at;

-- 3. Pending Payments View
-- Shows all pending contributions that need to be paid
CREATE OR REPLACE VIEW pending_payments AS
SELECT 
    c.id as contribution_id,
    c.group_id,
    ag.name as group_name,
    c.user_id,
    u.full_name as user_name,
    u.email as user_email,
    c.amount,
    c.due_date,
    c.payment_method,
    c.created_at as contribution_created,
    
    -- Days calculation
    CURRENT_DATE - c.due_date as days_since_due,
    CASE 
        WHEN c.due_date < CURRENT_DATE THEN 'overdue'
        WHEN c.due_date = CURRENT_DATE THEN 'due_today'
        WHEN c.due_date <= CURRENT_DATE + INTERVAL '7 days' THEN 'due_soon'
        ELSE 'future'
    END as urgency_status,
    
    -- Group context
    ag.contribution_amount as expected_amount,
    ag.frequency,
    gm.payment_position,
    gm.role as member_role,
    
    -- User context
    u.phone_number,
    u.preferred_payment_method,
    u.verification_status

FROM contributions c
JOIN ajo_groups ag ON c.group_id = ag.id
JOIN users u ON c.user_id = u.id
JOIN group_members gm ON c.group_id = gm.group_id AND c.user_id = gm.user_id
WHERE c.status = 'pending'
ORDER BY c.due_date ASC, ag.name, u.full_name;

-- 4. Overdue Contributions View
-- Focuses specifically on overdue payments with escalation information
CREATE OR REPLACE VIEW overdue_contributions AS
SELECT 
    c.id as contribution_id,
    c.group_id,
    ag.name as group_name,
    c.user_id,
    u.full_name as user_name,
    u.email as user_email,
    u.phone_number,
    c.amount,
    c.due_date,
    c.created_at as contribution_created,
    
    -- Overdue analysis
    CURRENT_DATE - c.due_date as days_overdue,
    CASE 
        WHEN CURRENT_DATE - c.due_date <= 7 THEN 'recently_overdue'
        WHEN CURRENT_DATE - c.due_date <= 30 THEN 'moderately_overdue'
        WHEN CURRENT_DATE - c.due_date <= 90 THEN 'seriously_overdue'
        ELSE 'critically_overdue'
    END as overdue_severity,
    
    -- Member context
    gm.payment_position,
    gm.role as member_role,
    gm.join_date,
    
    -- Group context
    ag.contribution_amount as expected_amount,
    ag.frequency,
    ag.max_members,
    
    -- Member payment history
    (SELECT COUNT(*) FROM contributions c2 
     WHERE c2.user_id = c.user_id AND c2.group_id = c.group_id AND c2.status = 'paid') as previous_payments,
    (SELECT COUNT(*) FROM contributions c2 
     WHERE c2.user_id = c.user_id AND c2.group_id = c.group_id AND c2.status = 'overdue') as total_overdue,
    
    -- Risk assessment
    CASE 
        WHEN (SELECT COUNT(*) FROM contributions c2 
              WHERE c2.user_id = c.user_id AND c2.status = 'overdue') > 3 THEN 'high_risk'
        WHEN (SELECT COUNT(*) FROM contributions c2 
              WHERE c2.user_id = c.user_id AND c2.status = 'overdue') > 1 THEN 'medium_risk'
        ELSE 'low_risk'
    END as member_risk_level

FROM contributions c
JOIN ajo_groups ag ON c.group_id = ag.id
JOIN users u ON c.user_id = u.id
JOIN group_members gm ON c.group_id = gm.group_id AND c.user_id = gm.user_id
WHERE c.status = 'overdue' OR (c.status = 'pending' AND c.due_date < CURRENT_DATE)
ORDER BY days_overdue DESC, c.amount DESC;

-- 5. Group Performance Dashboard View
-- High-level metrics for group performance monitoring
CREATE OR REPLACE VIEW group_performance_dashboard AS
SELECT 
    ag.id as group_id,
    ag.name as group_name,
    ag.status as group_status,
    ag.contribution_amount,
    ag.frequency,
    
    -- Member metrics
    COUNT(DISTINCT gm.user_id) as total_members,
    COUNT(DISTINCT CASE WHEN gm.status = 'active' THEN gm.user_id END) as active_members,
    ROUND(COUNT(DISTINCT CASE WHEN gm.status = 'active' THEN gm.user_id END)::numeric / ag.max_members::numeric * 100, 1) as capacity_utilization_percent,
    
    -- Recent contribution performance (last 30 days)
    COUNT(CASE WHEN c.created_at >= CURRENT_DATE - INTERVAL '30 days' AND c.status = 'paid' THEN c.id END) as recent_payments,
    COUNT(CASE WHEN c.due_date >= CURRENT_DATE - INTERVAL '30 days' AND c.due_date <= CURRENT_DATE THEN c.id END) as recent_due,
    
    -- Performance ratios
    CASE 
        WHEN COUNT(CASE WHEN c.due_date >= CURRENT_DATE - INTERVAL '30 days' AND c.due_date <= CURRENT_DATE THEN c.id END) > 0
        THEN ROUND(
            COUNT(CASE WHEN c.created_at >= CURRENT_DATE - INTERVAL '30 days' AND c.status = 'paid' THEN c.id END)::numeric /
            COUNT(CASE WHEN c.due_date >= CURRENT_DATE - INTERVAL '30 days' AND c.due_date <= CURRENT_DATE THEN c.id END)::numeric * 100, 1
        )
        ELSE 0
    END as recent_payment_rate_percent,
    
    -- Financial health
    COALESCE(SUM(CASE WHEN c.status = 'paid' THEN c.amount ELSE 0 END), 0) as total_collected,
    COALESCE(SUM(CASE WHEN c.status = 'overdue' THEN c.amount ELSE 0 END), 0) as total_overdue,
    COUNT(CASE WHEN c.status = 'overdue' THEN c.id END) as overdue_count,
    
    -- Distribution progress
    COUNT(CASE WHEN d.status = 'completed' THEN d.id END) as completed_distributions,
    COUNT(DISTINCT CASE WHEN d.status = 'completed' THEN d.recipient_id END) as unique_recipients,
    
    -- Health score (0-100)
    GREATEST(0, LEAST(100, 
        CASE 
            WHEN COUNT(c.id) = 0 THEN 50  -- New group, neutral score
            ELSE 
                -- Base score from payment rate
                (COUNT(CASE WHEN c.status = 'paid' THEN c.id END)::numeric / COUNT(c.id)::numeric * 60) +
                -- Bonus for low overdue rate
                (GREATEST(0, 40 - COUNT(CASE WHEN c.status = 'overdue' THEN c.id END)::numeric / COUNT(c.id)::numeric * 40)) +
                -- Penalty for high member turnover would go here
                0
        END
    )) as health_score,
    
    -- Activity indicators
    ag.created_at as group_created,
    MAX(c.created_at) as last_contribution,
    MAX(d.created_at) as last_distribution,
    COUNT(CASE WHEN c.created_at >= CURRENT_DATE - INTERVAL '7 days' THEN c.id END) as activity_last_week

FROM ajo_groups ag
LEFT JOIN group_members gm ON ag.id = gm.group_id
LEFT JOIN contributions c ON ag.id = c.group_id
LEFT JOIN distributions d ON ag.id = d.group_id
GROUP BY ag.id, ag.name, ag.status, ag.contribution_amount, ag.frequency, ag.max_members, ag.created_at
ORDER BY health_score DESC, total_collected DESC;

-- Create indexes to optimize view performance
-- These indexes will speed up the most common queries used by the views

-- Index for contribution lookups by group and status
CREATE INDEX IF NOT EXISTS idx_contributions_group_status_due 
ON contributions(group_id, status, due_date);

-- Index for contribution lookups by user and status  
CREATE INDEX IF NOT EXISTS idx_contributions_user_status_created
ON contributions(user_id, status, created_at);

-- Index for distribution lookups by group and status
CREATE INDEX IF NOT EXISTS idx_distributions_group_status_date
ON distributions(group_id, status, distribution_date);

-- Index for group member lookups by status
CREATE INDEX IF NOT EXISTS idx_group_members_status_join
ON group_members(group_id, status, join_date);

-- Composite index for overdue analysis
CREATE INDEX IF NOT EXISTS idx_contributions_overdue_analysis
ON contributions(status, due_date, created_at) 
WHERE status IN ('pending', 'overdue');

-- Index for user financial summaries
CREATE INDEX IF NOT EXISTS idx_users_verification_created
ON users(verification_status, created_at);

-- Comments for documentation
COMMENT ON VIEW group_financial_summary IS 'Comprehensive financial overview for each Ajo group including member count, contribution statistics, and distribution tracking';
COMMENT ON VIEW member_contribution_summary IS 'Individual member performance across all groups including payment rates, overdue analysis, and net position';
COMMENT ON VIEW pending_payments IS 'All pending contributions with urgency status and member context for payment follow-up';
COMMENT ON VIEW overdue_contributions IS 'Overdue payments with severity analysis and risk assessment for collection efforts';
COMMENT ON VIEW group_performance_dashboard IS 'High-level group performance metrics with health scores for monitoring and management';

-- Grant appropriate permissions (adjust as needed for your security model)
-- GRANT SELECT ON group_financial_summary TO ajo_app_role;
-- GRANT SELECT ON member_contribution_summary TO ajo_app_role;
-- GRANT SELECT ON pending_payments TO ajo_app_role;
-- GRANT SELECT ON overdue_contributions TO ajo_app_role;
-- GRANT SELECT ON group_performance_dashboard TO ajo_app_role;