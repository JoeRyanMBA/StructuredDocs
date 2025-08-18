-- PostgreSQL import script
-- Run this on PythonAnywhere's PostgreSQL console

\copy collection_topic_tree FROM 'collection_topic_tree.csv' DELIMITER ',' CSV HEADER;
\copy collections FROM 'collections.csv' DELIMITER ',' CSV HEADER;
\copy import_documents FROM 'import_documents.csv' DELIMITER ',' CSV HEADER;
\copy import_images FROM 'import_images.csv' DELIMITER ',' CSV HEADER;
\copy import_items FROM 'import_items.csv' DELIMITER ',' CSV HEADER;
\copy links FROM 'links.csv' DELIMITER ',' CSV HEADER;
\copy notifications FROM 'notifications.csv' DELIMITER ',' CSV HEADER;
\copy project_milestones FROM 'project_milestones.csv' DELIMITER ',' CSV HEADER;
\copy project_stakeholders FROM 'project_stakeholders.csv' DELIMITER ',' CSV HEADER;
\copy projects FROM 'projects.csv' DELIMITER ',' CSV HEADER;
\copy publication_nodes FROM 'publication_nodes.csv' DELIMITER ',' CSV HEADER;
\copy publications FROM 'publications.csv' DELIMITER ',' CSV HEADER;
\copy review_feedback FROM 'review_feedback.csv' DELIMITER ',' CSV HEADER;
\copy review_sequence_steps FROM 'review_sequence_steps.csv' DELIMITER ',' CSV HEADER;
\copy review_sequences FROM 'review_sequences.csv' DELIMITER ',' CSV HEADER;
\copy review_tokens FROM 'review_tokens.csv' DELIMITER ',' CSV HEADER;
\copy reviews FROM 'reviews.csv' DELIMITER ',' CSV HEADER;
\copy stakeholders FROM 'stakeholders.csv' DELIMITER ',' CSV HEADER;
\copy tags FROM 'tags.csv' DELIMITER ',' CSV HEADER;
\copy tasks FROM 'tasks.csv' DELIMITER ',' CSV HEADER;
\copy topic_links FROM 'topic_links.csv' DELIMITER ',' CSV HEADER;
\copy topics FROM 'topics.csv' DELIMITER ',' CSV HEADER;
\copy users FROM 'users.csv' DELIMITER ',' CSV HEADER;

-- Verify data
SELECT 'collection_topic_tree' as table_name, COUNT(*) as row_count FROM collection_topic_tree;
SELECT 'collections' as table_name, COUNT(*) as row_count FROM collections;
SELECT 'import_documents' as table_name, COUNT(*) as row_count FROM import_documents;
SELECT 'import_images' as table_name, COUNT(*) as row_count FROM import_images;
SELECT 'import_items' as table_name, COUNT(*) as row_count FROM import_items;
SELECT 'links' as table_name, COUNT(*) as row_count FROM links;
SELECT 'notifications' as table_name, COUNT(*) as row_count FROM notifications;
SELECT 'project_milestones' as table_name, COUNT(*) as row_count FROM project_milestones;
SELECT 'project_stakeholders' as table_name, COUNT(*) as row_count FROM project_stakeholders;
SELECT 'projects' as table_name, COUNT(*) as row_count FROM projects;
SELECT 'publication_nodes' as table_name, COUNT(*) as row_count FROM publication_nodes;
SELECT 'publications' as table_name, COUNT(*) as row_count FROM publications;
SELECT 'review_feedback' as table_name, COUNT(*) as row_count FROM review_feedback;
SELECT 'review_sequence_steps' as table_name, COUNT(*) as row_count FROM review_sequence_steps;
SELECT 'review_sequences' as table_name, COUNT(*) as row_count FROM review_sequences;
SELECT 'review_tokens' as table_name, COUNT(*) as row_count FROM review_tokens;
SELECT 'reviews' as table_name, COUNT(*) as row_count FROM reviews;
SELECT 'stakeholders' as table_name, COUNT(*) as row_count FROM stakeholders;
SELECT 'tags' as table_name, COUNT(*) as row_count FROM tags;
SELECT 'tasks' as table_name, COUNT(*) as row_count FROM tasks;
SELECT 'topic_links' as table_name, COUNT(*) as row_count FROM topic_links;
SELECT 'topics' as table_name, COUNT(*) as row_count FROM topics;
SELECT 'users' as table_name, COUNT(*) as row_count FROM users;
