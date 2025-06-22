-- Migration: Add end_date field to ajo_groups table
-- This field will store the calculated end date based on start_date + duration_months

-- Add the end_date column
ALTER TABLE ajo_groups 
ADD COLUMN end_date DATE;

-- Add a check constraint to ensure end_date is after start_date
ALTER TABLE ajo_groups 
ADD CONSTRAINT ajo_groups_end_date_check 
CHECK (end_date IS NULL OR end_date > start_date);

-- Create an index on end_date for performance (useful for querying active/expired groups)
CREATE INDEX idx_ajo_groups_end_date ON ajo_groups(end_date);

-- Update existing records to calculate end_date based on start_date + duration_months
UPDATE ajo_groups 
SET end_date = start_date + INTERVAL '1 month' * duration_months
WHERE end_date IS NULL;

-- Add a comment to document the field
COMMENT ON COLUMN ajo_groups.end_date IS 'Calculated end date of the group cycle (start_date + duration_months)';

-- Optional: Create a function to automatically calculate end_date when start_date or duration_months change
CREATE OR REPLACE FUNCTION calculate_group_end_date()
RETURNS TRIGGER AS $$
BEGIN
    -- Calculate end_date when start_date or duration_months is updated
    IF NEW.start_date IS NOT NULL AND NEW.duration_months IS NOT NULL THEN
        NEW.end_date := NEW.start_date + INTERVAL '1 month' * NEW.duration_months;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update end_date
CREATE TRIGGER trigger_calculate_group_end_date
    BEFORE INSERT OR UPDATE OF start_date, duration_months ON ajo_groups
    FOR EACH ROW
    EXECUTE FUNCTION calculate_group_end_date(); 