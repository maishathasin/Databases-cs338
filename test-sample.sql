-- Getting user applications
SELECT * FROM Applications WHERE applicant_id = 1;

-- Applying to jobs
INSERT INTO Applications (applicant_id, job_posting_id, application_date, status) VALUES (11, 13, '2024-06-21', 'Applied');

-- Search functionality for formatting sake in the .out file limited to 1 
SELECT * FROM JobPostings WHERE business_title LIKE '%Data Scientist%' LIMIT 1;

-- Update Application status
UPDATE Applications SET status = 'Offered' WHERE application_id = 1 AND job_posting_id = 1;

-- Delete Application
DELETE FROM Applications WHERE job_posting_id = 1 AND application_id = 1;

-- Show all job postings, for formatting sake limited to 1 
SELECT * FROM JobPostings Limit 1;