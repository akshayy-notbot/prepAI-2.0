-- SQL template for importing interview playbook data
-- Replace the VALUES with your actual data

INSERT INTO interview_playbooks (
    role, 
    skill, 
    seniority, 
    archetype, 
    interview_objective,
    evaluation_dimensions, 
    seniority_criteria, 
    good_vs_great_examples,
    pre_interview_strategy, 
    during_interview_execution, 
    post_interview_evaluation,
    created_at
) VALUES 
(
    'Product Manager',                    -- role
    'Product Sense',                      -- skill  
    'Mid-level',                          -- seniority
    'broad_design',                       -- archetype
    'Assess candidate ability to design products from scratch', -- interview_objective
    
    -- JSON fields (use single quotes and escape internal quotes)
    '{"problem_scoping": {"signals": ["asks clarifying questions"], "probes": ["What is the business goal?"]}}', -- evaluation_dimensions
    
    '{"mid_level": {"problem_scoping": "Should ask basic clarifying questions"}}', -- seniority_criteria
    
    '{"problem_scoping": {"good": "Asks basic questions", "great": "Asks detailed clarifying questions with context"}}', -- good_vs_great_examples
    
    -- Text fields (use single quotes and escape internal quotes)
    'Step 1: Select the most relevant Archetype for the Role X Skill X Seniority...', -- pre_interview_strategy
    
    'In-Interview Execution (45 minutes) My role is to be a collaborative guide...', -- during_interview_execution
    
    'Post-Interview Evaluation (15 minutes) Immediately after the interview...', -- post_interview_evaluation
    
    CURRENT_TIMESTAMP                     -- created_at
);

-- Add more INSERT statements for additional playbooks
-- INSERT INTO interview_playbooks (...) VALUES (...);
-- INSERT INTO interview_playbooks (...) VALUES (...);

-- Verify the import
SELECT COUNT(*) as total_playbooks FROM interview_playbooks;
SELECT role, skill, seniority, archetype FROM interview_playbooks ORDER BY role, skill, seniority;
