-- Keep only the admin user in the users table
DELETE FROM users WHERE name != 'admin' AND email != 'admin';

-- Clear all other tables (order matters due to foreign keys)
DELETE FROM notifications;
DELETE FROM links;
DELETE FROM topic_links;
DELETE FROM import_items;
DELETE FROM import_documents;
DELETE FROM import_images;
DELETE FROM publication_nodes;
DELETE FROM publications;
DELETE FROM project_stakeholders;
DELETE FROM project_milestones;
DELETE FROM collections;
DELETE FROM collection_topic_tree;
DELETE FROM tasks;
DELETE FROM stakeholders;
DELETE FROM topics;
DELETE FROM projects;
