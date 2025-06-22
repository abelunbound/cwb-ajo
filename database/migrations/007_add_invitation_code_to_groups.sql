-- Migration: Add invitation_code field to ajo_groups table
-- This field will store unique invitation codes for groups to enable member invitations
-- Task 27: Implement Group Creation Logic

-- Add the invitation_code column
ALTER TABLE ajo_groups 
ADD COLUMN invitation_code VARCHAR(10) UNIQUE;

-- Create an index on invitation_code for performance
CREATE INDEX idx_ajo_groups_invitation_code ON ajo_groups(invitation_code);

-- Add a comment to document the field
COMMENT ON COLUMN ajo_groups.invitation_code IS 'Unique invitation code for group member invitations (8 characters)';

-- Update existing groups with unique invitation codes
-- Note: This uses a simple approach for existing data. In production, you might want more sophisticated logic.
UPDATE ajo_groups 
SET invitation_code = UPPER(SUBSTRING(MD5(RANDOM()::TEXT || id::TEXT) FROM 1 FOR 8))
WHERE invitation_code IS NULL;

-- Make invitation_code NOT NULL after updating existing records
ALTER TABLE ajo_groups 
ALTER COLUMN invitation_code SET NOT NULL; 