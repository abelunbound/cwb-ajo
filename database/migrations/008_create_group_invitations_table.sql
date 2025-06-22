-- Migration: Create ajo_group_invitations table
-- This table manages group invitation workflow for Task 29
-- Enables group admins to invite members via unique invitation codes

-- Create the main invitations table
CREATE TABLE ajo_group_invitations (
    id SERIAL PRIMARY KEY,
    group_id INTEGER NOT NULL REFERENCES ajo_groups(id) ON DELETE CASCADE,
    inviter_user_id INTEGER NOT NULL,
    invitee_email VARCHAR(255) NOT NULL,
    invitation_code VARCHAR(50) UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'declined', 'expired')),
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    accepted_at TIMESTAMP,
    declined_at TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_invitation_code ON ajo_group_invitations(invitation_code);
CREATE INDEX idx_invitee_email ON ajo_group_invitations(invitee_email);
CREATE INDEX idx_group_id ON ajo_group_invitations(group_id);
CREATE INDEX idx_status ON ajo_group_invitations(status);
CREATE INDEX idx_expires_at ON ajo_group_invitations(expires_at);

-- Add comments for documentation
COMMENT ON TABLE ajo_group_invitations IS 'Group invitation management system for Task 29';
COMMENT ON COLUMN ajo_group_invitations.invitation_code IS 'Unique code used in invitation links (format: inv_xxxxxxxxxx)';
COMMENT ON COLUMN ajo_group_invitations.status IS 'Invitation status: pending, accepted, declined, expired';
COMMENT ON COLUMN ajo_group_invitations.expires_at IS 'Invitation expiration timestamp (default: 7 days from creation)';

-- Create function to generate unique invitation codes
CREATE OR REPLACE FUNCTION generate_invitation_code()
RETURNS TEXT AS $$
DECLARE
    new_code TEXT;
    code_exists BOOLEAN;
BEGIN
    LOOP
        -- Generate invitation code with format: inv_xxxxxxxxxx (14 chars total)
        new_code := 'inv_' || UPPER(SUBSTRING(MD5(RANDOM()::TEXT || CURRENT_TIMESTAMP::TEXT) FROM 1 FOR 10));
        
        -- Check if code already exists
        SELECT EXISTS(SELECT 1 FROM ajo_group_invitations WHERE invitation_code = new_code) INTO code_exists;
        
        -- Exit loop if code is unique
        IF NOT code_exists THEN
            EXIT;
        END IF;
    END LOOP;
    
    RETURN new_code;
END;
$$ LANGUAGE plpgsql;

-- Create function to automatically expire old invitations
CREATE OR REPLACE FUNCTION expire_old_invitations()
RETURNS INTEGER AS $$
DECLARE
    expired_count INTEGER;
BEGIN
    UPDATE ajo_group_invitations 
    SET status = 'expired'
    WHERE status = 'pending' 
    AND expires_at < CURRENT_TIMESTAMP;
    
    GET DIAGNOSTICS expired_count = ROW_COUNT;
    RETURN expired_count;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically set accepted_at/declined_at timestamps
CREATE OR REPLACE FUNCTION update_invitation_timestamps()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'accepted' AND OLD.status != 'accepted' THEN
        NEW.accepted_at := CURRENT_TIMESTAMP;
    ELSIF NEW.status = 'declined' AND OLD.status != 'declined' THEN
        NEW.declined_at := CURRENT_TIMESTAMP;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_invitation_timestamps
    BEFORE UPDATE ON ajo_group_invitations
    FOR EACH ROW
    EXECUTE FUNCTION update_invitation_timestamps(); 