-- Migration: 004_create_payments_table.sql
-- Purpose: Complete Task 11 by adding the payments table for external payment processing
-- Date: 2025-01-21

-- Create payments table for external payment processor transactions
CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    
    -- Link to internal transactions (optional - one or the other)
    contribution_id INTEGER REFERENCES contributions(id),
    distribution_id INTEGER REFERENCES distributions(id),
    
    -- Payment provider details
    provider VARCHAR(50) NOT NULL,  -- 'stripe', 'paypal', 'bank_transfer'
    provider_payment_id VARCHAR(255) UNIQUE,  -- External payment ID from provider
    provider_transaction_id VARCHAR(255),     -- External transaction ID
    
    -- Payment details
    amount NUMERIC(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'GBP',
    payment_method VARCHAR(50),  -- 'card', 'bank_account', 'paypal'
    
    -- Status tracking
    status VARCHAR(50) DEFAULT 'pending',  -- 'pending', 'processing', 'completed', 'failed', 'refunded'
    payment_intent_status VARCHAR(50),     -- Provider-specific status
    
    -- Verification and security
    verification_status VARCHAR(50) DEFAULT 'unverified',
    fraud_score DECIMAL(3,2),
    risk_level VARCHAR(20),
    
    -- Timing
    initiated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Error handling
    failure_reason TEXT,
    retry_count INTEGER DEFAULT 0,
    
    -- Audit trail
    webhook_data JSONB,  -- Store provider webhook data
    metadata JSONB,      -- Additional payment metadata
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_payments_contribution_id ON payments(contribution_id);
CREATE INDEX IF NOT EXISTS idx_payments_distribution_id ON payments(distribution_id);
CREATE INDEX IF NOT EXISTS idx_payments_provider_payment_id ON payments(provider_payment_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
CREATE INDEX IF NOT EXISTS idx_payments_created_at ON payments(created_at);

-- Add constraints
ALTER TABLE payments ADD CONSTRAINT chk_payments_amount_positive CHECK (amount > 0);
ALTER TABLE payments ADD CONSTRAINT chk_payments_currency_valid CHECK (currency IN ('GBP', 'USD', 'EUR'));
ALTER TABLE payments ADD CONSTRAINT chk_payments_status_valid 
    CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'refunded', 'cancelled'));
ALTER TABLE payments ADD CONSTRAINT chk_payments_verification_status_valid 
    CHECK (verification_status IN ('unverified', 'verified', 'failed', 'pending'));

-- Ensure either contribution_id or distribution_id is set (not both, not neither)
ALTER TABLE payments ADD CONSTRAINT chk_payments_transaction_link 
    CHECK ((contribution_id IS NOT NULL AND distribution_id IS NULL) OR 
           (contribution_id IS NULL AND distribution_id IS NOT NULL));

-- Add trigger for updated_at timestamp
CREATE OR REPLACE FUNCTION update_payments_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_payments_updated_at
    BEFORE UPDATE ON payments
    FOR EACH ROW
    EXECUTE FUNCTION update_payments_updated_at();

-- Comments for documentation
COMMENT ON TABLE payments IS 'External payment processor transactions (Stripe, PayPal, bank transfers)';
COMMENT ON COLUMN payments.contribution_id IS 'Links to contributions table for incoming payments';
COMMENT ON COLUMN payments.distribution_id IS 'Links to distributions table for outgoing payments';
COMMENT ON COLUMN payments.provider IS 'Payment provider name (stripe, paypal, bank_transfer)';
COMMENT ON COLUMN payments.provider_payment_id IS 'Unique payment ID from external provider';
COMMENT ON COLUMN payments.webhook_data IS 'JSON data from provider webhooks for audit trail';
COMMENT ON COLUMN payments.metadata IS 'Additional payment metadata for flexibility'; 