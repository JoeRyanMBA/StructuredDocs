# StructuredDocs User Guide

StructuredDocs is a workspace for organizing, writing, reviewing, and publishing documentation. This guide covers the features available in the application. Your role and your organization's configuration may affect which pages and actions you can access.

## Start Here

Sign in with the account provided by your administrator. Use the navigation menu to move between sections; on smaller screens, open the menu from the header. The Home page summarizes projects, collections, topics, reviews, pending actions, recent import activity, and calendar events. Select a metric or quick action to open the corresponding area.

Use **Profile** to manage your account details and follow any password setup or reset link sent to you. Sign out when you finish on a shared device. If your session expires, sign in again.

## How Content Is Organized

StructuredDocs uses a three-level content hierarchy:

- **Projects** group work around an initiative, product, or program. A project can have collections, stakeholders, milestones, and tasks.
- **Collections** group related topics, often for a document set, audience, or release. A collection belongs to a project and has a unique collection ID or form number.
- **Topics** are the individual articles or content units. A topic can be included in collections and publications and can move through review and approval.

Some resources, such as tags, snippets, images, and links, can be reused across topics.

## Projects and Collections

### Projects

Open **Projects** to search and filter projects by status, review project summaries, and create or edit projects. Project status options include Planning, Active, On Hold, and Completed. Open a project's timeline to review its scheduled work. The project area also links to tasks, milestones, stakeholders, and tags.

### Collections

Open **Collections** to browse, create, edit, or open collections. Creating a collection requires a parent project, a name, and a unique collection ID/form number; a description and status can also be set. Open a collection's organize view to work with its topic membership and ordering. Collections are also a common destination for document imports and a source for publications.

Administrators may archive or restore projects and collections. Archiving removes an item from normal active work without treating it as a permanent deletion. Administrators can review archived items from the Admin area.

## Writing and Managing Topics

Open **Author** for writing progress, topic counts, search and status filters, and quick links to create content or browse reusable images and links. Open **Topics** to browse the broader topic list. Select a topic to read it or open it in the editor.

When creating or editing a topic, add its title and content, then save your changes. The editor supports rich-text authoring; available formatting controls depend on the editor configuration. You can organize topics with project/collection associations and tags. Topic content can include links, images, reusable snippets, and configured variables. Use preview or the read view to check the result before sending it for review or including it in a publication.

Topic status indicates where the content is in its lifecycle. Draft topics are still being prepared; submitted topics may be pending or in review; reviewers can approve content or request revisions. The exact status labels shown depend on the workflow.

## Importing Documents

Open **Collections > Import** (or choose Import from the authoring area) and select the import mode that matches your files:

1. **Import Topic** creates one topic from one Markdown (`.md`/`.markdown`) or Word (`.docx`) file. Review and edit its content before saving it.
2. **Collection** imports one document as a collection, turning its headings into topics. Choose the destination project and provide the collection name and ID/form number.
3. **Create Collection** imports multiple files as individual topics in a new collection. Choose the destination project and provide the collection details.

After submission, use the Import Dashboard to see recent imports and imports awaiting review. Open an import to review the staged content, then use Import History to find earlier import activity. For the best results with Word documents, use Word heading styles to express section hierarchy and embed images in the document rather than linking to them.

For supported formats, image handling, hierarchy, and troubleshooting, see the [Import Guide](import-guide.md).

## Reviews and Feedback

Authors can submit a draft topic for review from the Author area or the review workflow. Select one or more reviewers, set a due date (and priority where offered), and add optional instructions. For reviewers who should act in a specific order, use sequential review setup and arrange the steps before starting the sequence.

Open **Reviews** to see review activity and metrics. **Tasks** lists review work; **History** shows completed work. Search by topic or reviewer and filter by status or urgent/overdue items. Depending on the review's status, available actions may include viewing details, following up, reassigning, cancelling, or incorporating feedback.

Reviewers can inspect the topic, compare revisions where available, leave feedback, and submit a recommendation. Authors use **Incorporate Feedback** to address requested changes and can then submit the revised topic again. External reviewers may receive a time-limited review link that does not require a StructuredDocs account; treat the link as private and use it only for the intended review.

See the [Review Workflow Guide](REVIEW_WORKFLOW_GUIDE.md) for status details and sequential review steps.

## Tasks, Milestones, Stakeholders, and Tags

- **Tasks** track work associated with a project, collection, or topic. Create a task with a title and optional details, assignee, priority, and due date. Search and filter tasks by status, priority, and association. Move tasks through To Do, In Progress, Review, and Completed; cancelled tasks may also appear. Overdue tasks are highlighted.
- **Milestones** record significant dates and progress for project work. Use the milestone list and project calendar/timeline to keep upcoming dates visible.
- **Stakeholders** are people involved in project work, reviews, or approvals. Manage stakeholder details and use the appropriate reviewer configuration when assigning reviews.
- **Tags** label and group content. Tags can also identify audiences for snippets and publication exports.

The available edit and delete actions can differ by role. Check with an administrator if a resource or action is unavailable.

## Snippets and Reusable Resources

### Snippets

Open **Snippets** to create and maintain reusable content blocks. A snippet has a title, content, and optional audience tags. Edit its content in Markdown or WYSIWYG mode, or use Preview to check it. The library shows where a snippet is used; snippets already used by topics cannot be deleted from the library. Insert snippets into topic content using the editor's snippet controls. When exporting a publication, audience-tag selection determines which tagged snippets are included.

### Images and Links

The Author area links to image and link libraries. Browse or search existing resources while editing; where offered, you can upload an image or insert an image/link by URL. Add descriptive alternative text to images where possible. Imported images and uploaded assets may be subject to your organization's storage configuration.

## Publishing

Open **Collections > Publish** to manage publications. Create or edit a publication, arrange the content it includes, and preview it before release. A saved publication snapshot captures the selected content at that point in time. If source topics change, use **Refresh Publication** to update the publication from its sources before exporting.

Available outputs depend on your deployment and publication setup. The app supports PDF and mobile knowledge base exports; HTML publication output may also be enabled. Select audience tags when prompted to control which audience-specific snippets are included. Use the publication dashboard to view, preview, edit, refresh, and export publications.

## Notifications and Account Help

Application notifications appear in the interface when enabled. Open a notification to review it and mark it read where that option is provided. Administrators manage system notifications. Use the in-app help icons for page-specific guidance where available; contact your administrator for access, account, or configuration problems.

## Administrator Features

Administrators see additional options in **Admin**. Depending on the installation, these can include:

- Managing users and account access.
- Application settings, shared variables, and notification management.
- System logs, audit history, and performance metrics.
- Reviewing submitted feedback and bug reports.
- Maintaining help links and using administrative find/replace tools.
- Restoring archived projects, collections, feedback, or bug reports.

Admin pages and actions are restricted to administrator accounts. UI catalogs, if present, are design references rather than normal content workflows.

## Tips and Troubleshooting

- Use search and filters on list pages to narrow down results; clear filters if an expected item is missing.
- Check the item's status and its project or collection association when locating content.
- If an import is still being processed, check the Import Dashboard or History before uploading the same file again.
- If a publication does not contain the latest topic edits, refresh its snapshot and preview it again.
- If images are missing after a Word import, confirm they were embedded in the source file and consult the [Import Guide](import-guide.md).
- If a page fails to load, refresh it once. If the problem continues, note the page and any displayed error and contact your administrator.
- If a menu, reviewer, or action is missing, it may require a different role or additional administrator configuration.

## Related Documentation

- [Import Guide](import-guide.md)
- [Review Workflow Guide](REVIEW_WORKFLOW_GUIDE.md)
- [Documentation Hub](README.md)
