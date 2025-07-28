# Project-Based Review System Design

## 🎯 **Overview**

The StructuredDocs application now features a comprehensive **Project-Based Review System** that allows organizations to manage document reviews within the context of specific projects, with defined stakeholders, milestones, and workflow processes.

## 🏗️ **System Architecture**

### **Core Components**

1. **Projects** - Central organizing unit containing:
   - Collections and topics
   - Project-specific stakeholders  
   - Milestones and deadlines
   - Review workflows

2. **Stakeholders** - Project team members with defined roles:
   - Project Manager
   - Subject Matter Expert  
   - Reviewer
   - Stakeholder

3. **Project-Based Reviews** - Review assignments within project context:
   - Topic assignment to specific stakeholder
   - Due dates tied to project milestones
   - Project-specific review workflows

## 📊 **Database Schema**

### **New Tables**

#### `projects`
```sql
- id (Primary Key)
- name (Project title)
- description (Project description)
- status (planning, active, review, completed, on_hold)
- start_date
- target_completion
- created_at, updated_at
```

#### `project_stakeholders`
```sql
- id (Primary Key)
- project_id (Foreign Key to projects)
- name (Stakeholder name)
- email (Contact email)
- role (project_manager, subject_matter_expert, reviewer, stakeholder)
- can_review (Boolean - can this person review topics?)
- notes (Role-specific notes)
- created_at
```

#### `project_milestones`
```sql
- id (Primary Key)
- project_id (Foreign Key to projects)
- title (Milestone name)
- description
- due_date
- status (pending, in_progress, completed, delayed)
- completion_date
- created_at
```

#### `topic_reviews`
```sql
- id (Primary Key)
- project_id (Foreign Key to projects)
- topic_id (Foreign Key to topics)
- assigned_stakeholder_id (Foreign Key to project_stakeholders)
- status (pending, in_review, approved, rejected, revision_requested)
- due_date
- submitted_at, reviewed_at
- submitter_notes, reviewer_comments
- created_at, updated_at
```

### **Updated Tables**

#### `collections`
- Added `project_id` (Foreign Key to projects)
- Collections can now belong to specific projects

#### `topics`
- Added `current_review_id` (Foreign Key to topic_reviews)
- Links topics to their current review status

## 🔌 **API Endpoints**

### **Project Management**
```
GET    /api/projects/                    # List all projects
GET    /api/projects/{id}                # Get project details with stakeholders/milestones
POST   /api/projects/                    # Create new project
PUT    /api/projects/{id}                # Update project
DELETE /api/projects/{id}                # Delete project
```

### **Stakeholder Management**
```
GET    /api/projects/{id}/stakeholders   # Get project stakeholders
POST   /api/projects/{id}/stakeholders   # Add stakeholder to project
PUT    /api/projects/{id}/stakeholders/{stakeholder_id}  # Update stakeholder
DELETE /api/projects/{id}/stakeholders/{stakeholder_id}  # Remove stakeholder
```

### **Review Management**
```
GET    /api/projects/{id}/reviews        # Get all reviews for project
POST   /api/projects/{id}/reviews        # Submit topic for project-based review
PUT    /api/projects/{id}/reviews/{review_id}  # Update review status
```

## 🎨 **User Interface**

### **Projects Dashboard**
- **Project Cards**: Visual overview of all projects with status indicators
- **Project Selection**: Click to view detailed project information
- **Quick Stats**: Stakeholder count, collection count, active reviews
- **Status Badges**: Visual project status (Planning, Active, Review, Completed, On Hold)

### **Project Details Panel**
- **Overview**: Project description, dates, status
- **Stakeholders**: List of team members with roles and review permissions
- **Milestones**: Project deadlines and completion tracking
- **Active Reviews**: Current review assignments and status

### **Enhanced Review Modal**
When submitting a topic for review:

1. **Project Selection**: Choose which project context to use
2. **Stakeholder Assignment**: Select from project stakeholders who can review
3. **Due Date**: Set review deadline (with validation)
4. **Review Notes**: Context and instructions for reviewer

### **Stakeholder Management**
- **Add Stakeholders**: Form to add team members with roles
- **Role Assignment**: Define stakeholder responsibilities
- **Review Permissions**: Control who can review topics
- **Contact Information**: Email and notes for each stakeholder

## 🔄 **Review Workflow**

### **Traditional Workflow (Before)**
```
Author → [Global Reviewer List] → Topic Review → Email/External System
```

### **Project-Based Workflow (After)**
```
Author → [Select Project] → [Project Stakeholders] → Project Review → Internal Tracking
```

### **Benefits**
1. **Context-Aware**: Reviews tied to specific project goals
2. **Stakeholder Management**: Clear definition of team roles
3. **Deadline Tracking**: Due dates aligned with project milestones
4. **Self-Contained**: No external system dependencies
5. **Audit Trail**: Complete review history within project context

## 🚀 **Implementation Status**

### ✅ **Completed**
- Database models and schema design
- Backend API endpoints (placeholder implementations)
- Frontend Projects management interface
- Enhanced review modal with project selection
- Navigation integration

### 🔄 **In Progress**
- Database migration scripts
- Full API implementation with database integration
- Milestone management interface
- Review status dashboard

### 📋 **Next Steps**
1. **Database Migration**: Implement database schema changes
2. **API Integration**: Connect frontend to fully functional backend
3. **Testing**: Populate with realistic project data
4. **Milestone Management**: Add milestone creation and tracking
5. **Reporting**: Project progress and review metrics

## 🧪 **Testing the System**

### **Current Functionality**
1. **Browse Projects**: Navigate to `/projects` to see project dashboard
2. **Create Projects**: Use "New Project" button to create projects
3. **Manage Stakeholders**: Add team members with defined roles
4. **Project-Based Reviews**: Enhanced review modal with project context

### **Sample Test Data**
- **Project**: "Census 2030 Survey Methodology"
- **Stakeholders**: Project Manager, Subject Matter Experts, Reviewers
- **Milestones**: Framework Design, Data Collection Protocols, Final Documentation

## 📖 **User Guide**

### **For Project Managers**
1. **Create Project**: Define project scope, dates, and description
2. **Add Stakeholders**: Invite team members and define their roles
3. **Set Milestones**: Establish key deadlines and deliverables
4. **Monitor Reviews**: Track review assignments and progress

### **For Authors**
1. **Select Project**: Choose project context when submitting for review
2. **Assign Reviewer**: Select from project stakeholders
3. **Set Due Date**: Align with project milestones
4. **Provide Context**: Add specific instructions for reviewer

### **For Reviewers**
1. **Project Dashboard**: View assigned reviews by project
2. **Review Context**: Understand review within project scope
3. **Deadline Awareness**: See how review fits project timeline
4. **Team Communication**: Contact other project stakeholders

## 🔒 **Security & Permissions**

### **Role-Based Access**
- **Project Manager**: Full project management capabilities
- **Subject Matter Expert**: Review content within expertise area
- **Reviewer**: Review assigned topics
- **Stakeholder**: View project progress, limited editing

### **Data Isolation**
- Projects maintain separate stakeholder lists
- Reviews are isolated within project context
- No cross-project data exposure without explicit permissions

## 🎯 **Business Value**

### **Organizational Benefits**
1. **Improved Accountability**: Clear assignment of review responsibilities
2. **Better Project Tracking**: Reviews aligned with project goals
3. **Reduced Dependencies**: Self-contained review system
4. **Enhanced Collaboration**: Project-specific communication
5. **Audit Compliance**: Complete review history and tracking

### **User Benefits**
1. **Context Clarity**: Reviews understood within project scope
2. **Efficient Assignment**: Relevant stakeholders for each topic
3. **Deadline Management**: Review dates tied to project milestones
4. **Team Visibility**: Clear view of project team and roles
5. **Streamlined Workflow**: No external system coordination needed

This project-based approach transforms the review system from a simple assignment mechanism into a comprehensive project management tool that supports organizational workflows while maintaining independence from external systems.
