# StructuredDocs Workflow

StructuredDocs helps authors organize content into projects, collections, and topics, then review and publish that content. Sign in with the account provided by your administrator. Your role and your organization's configuration determine which pages and actions are available. In the navigation, **Projects** contains tasks, milestones, stakeholders, and tags; **Collections** contains collection, import, and publish pages; **Author** contains topics and snippets; and **Reviews** contains review tasks and history.

## Create a project

Open **Projects** and select **Create Project**. Enter a project name, choose a status, and optionally add a description. Select **Next** to save the project and continue through the setup steps. The guided setup lets you add stakeholders and milestones now or skip either step and add them later.

### Add stakeholders to a project

During project setup, select an existing stakeholder and a project role, then choose **Add Selected**. To add someone new, enter their name and email, select a role, and choose **Add Stakeholder**. When finished, select **Add Stakeholders** to continue or **Not Now** to skip. You can also manage stakeholders from **Projects > Stakeholders** and edit a project later.

### Add milestones to a project

In the project setup milestone step, enter a name, optional date, and status for each milestone. Select **Add Milestone** to add another row, then choose **Add Milestones** to finish or **Not Now** to skip. Later, use **Projects > Milestones** to create or edit milestones; each milestone must be associated with a project.

## Create a collection

A collection groups related topics and belongs to a project. It has a name and a unique Collection ID (Form Number). Create a collection from **Collections** or import content into one from **Collections > Import**.

### Create a new collection

From **Collections**, select **Create Collection**. Choose a project, enter a collection name and unique ID, and optionally add a subtitle and status. The ID accepts letters, numbers, hyphens, and underscores. Select **Create Collection**, then open the collection to organize its topics.

### Import a document as a collection

Open **Collections > Import**, choose **Collection**, and select Markdown or Word (`.docx`) as the source format. Choose the project, enter the collection name and unique ID, and select one document. The document's headings are used to create topics; review the imported content before completing the import. Word heading styles help preserve the intended hierarchy.

### Import multiple files as a collection

On **Collections > Import**, choose **Create Collection**. Select the project and provide the new collection's name and unique ID, then choose multiple Markdown or Word files. Each file becomes one topic in the new collection. Review the import results before using the collection.

## Author a topic

Open **Author > Topics** and create a topic, or open an existing topic to edit it. Enter a title and content, then select **Create Topic** or **Update Topic** to save. Use the **Markdown** mode for raw Markdown, **WYSIWYG** for visual editing, or **Preview** to inspect rendered content. Existing topics can also be organized with tags and project or collection associations.

### Adding text

Type in the Markdown or WYSIWYG editor. The toolbars provide bold, italic, code, headings, lists, and tables. In Markdown mode, use Markdown syntax or the toolbar to insert formatting. In WYSIWYG mode, select text before applying a formatting control. Save the topic when your edits are ready.

### Insert an image

In the editor, choose **Image** or **Insert Image**. Select **By URL** to enter an image URL and alternative text, **Browse** to find an image already in the library, or **Upload** to add an image file. Select or upload the image and insert it into the topic. Descriptive alternative text helps readers who cannot see the image.

### Set the size of an image

In WYSIWYG mode, select the image. Use **Image size** to choose **Original size**, **25%**, **50%**, **75%**, or **Full width**. You can also drag the resize handle shown on a selected image for a custom size. Full-width images cannot use text-side wrapping.

### Set the alignment of an image

Select an image in WYSIWYG mode and choose **Align**, then select left, center, or right. Alignment is available when wrapping is set to **Above and below** or **Watermark**; for side-wrapped images, the wrapping option controls which side the image occupies.

### Set the wrapping for an image

Select an image and open **Wrapping**. Choose **Above and below** to keep text above and below the image, **Text left of image** or **Text right of image** to place text beside it, or **Watermark (behind text)** to put it behind text. Side wrapping is unavailable when the image is set to full width.

### Insert a link

Choose **Link** in the editor toolbar. Enter display text and a URL in **Manual** mode, or switch to **Existing** to search for a saved link. Select **Insert Link** to add it to the topic.

### Insert a snippet

Choose **Insert Snippet** in the editor, search or browse the available snippets, and select one to insert it. Snippets are reusable content blocks; changing a snippet can affect the topics that use it.

### Create a snippet in the topic editor

Choose **Create Snippet** in the topic editor. Enter a title and content, then select **Create Snippet**. To reuse or manage the snippet later, open **Author > Snippets**. A snippet can also be created directly in the Snippets Library.

### Spell check a topic

Select **Spell Check** in the editor toolbar to turn the editor's spellcheck on or off. The setting applies to the current editor session and uses the browser's spelling support.

### Preview a topic

Select **Preview** above the editor to see rendered content. If the topic contains audience-specific snippets, select audience tags in the preview controls to check the matching version. Return to Markdown or WYSIWYG to continue editing.

### Normalize pasted Word line breaks

The **Normalize pasted Word line breaks** checkbox is enabled by default. Leave it enabled to clean up soft line breaks when pasting Word text; turn it off if you need to preserve the pasted line breaks as-is. Your preference is saved in the browser.

## Create a task

Open **Projects > Tasks** and select **Create Task**. Enter a title and optionally add a description, status, priority, due date, assignee, association, and tags. Select **Create Task** to save. The task list supports search and status, priority, and association filters; available status changes depend on the task's current state.

### Associate a task with a project, collection, topic, or none of them

In the task form, use **Association** to choose **Project**, **Collection**, **Topic**, or **No Association**. If you choose a resource type, select the corresponding item from the field that appears. Choosing **No Association** leaves the task independent of content.

### Select tags for a task

In **Tags**, choose an existing tag from the selector. Selected tags appear in the form and can be removed before saving.

### Add tags to a task

If the tag does not exist, enter its name under **Or add a new tag** and select **Add**. The new tag is included when you save the task.

## Create a tag

Open **Projects > Tags** and select **Create New Tag**. Enter a unique name and any other requested details, then save. A tag can be assigned to supported content and used as an audience label for snippets and publication exports.

### Assign tags

Open a project, collection, topic, stakeholder, image, or link and use its **Tags** field when available. Search for an existing tag or create one inline. Tasks have their own tag controls in the task form.

### Filter by a tag

Use the tag filter on a list page that provides one, such as the Topics list. Select a tag to narrow the results; clear the filter to see the full list. Tag filtering varies by page.

### Rename a tag

In **Projects > Tags**, select the tag or choose **Edit**, change its name, and save. Renaming updates the tag wherever it is assigned.

### Delete a tag

In **Projects > Tags**, choose **Delete** for the tag and confirm. Deleting a tag removes its assignments from associated items.

## Create a snippet

Snippets are reusable content blocks. You can create them in the Snippets Library or while authoring a topic.

### Create a snippet in the Snippets Library

Open **Author > Snippets** and select **New Snippet**. Enter a title and content, using Markdown or WYSIWYG mode as needed; use **Preview** to check it. Save the snippet, then assign audience tags if appropriate. The library shows where a snippet is used, and a snippet already used by topics cannot be deleted from the library.

### Create a snippet from the topic editor

In a topic, choose **Create Snippet**, enter the snippet title and content, then select **Create Snippet**. Use **Insert Snippet** to place a saved snippet in a topic. To add audience tags or review usage, open the Snippets Library.

## Import content

Open **Collections > Import** or choose **Import Content** from the Author area. Choose the import type and source format, then follow the form to select the file or files. Markdown is preferred; Word documents must be `.docx`. Check the Import Dashboard or Import History if processing takes time, and avoid submitting the same file again while an import is still running.

### Import a topic

Choose **Import Topic**, select a Markdown or Word file, and submit it. The file becomes one topic. Review the imported topic and edit it before saving.

### Import a collection (document)

Choose **Collection**, select one document, then provide the destination project and collection details. The document's headings are split into topics in a new collection. Use Word heading styles to indicate section levels and embed images in the Word file when possible.

### Create a collection from imported files

Choose **Create Collection** to import several files as a new collection. Select the destination project and enter the collection name and unique ID, then select multiple source files. Each selected file becomes a topic in that collection.

For supported formats, image handling, hierarchy, and troubleshooting, see the [Import Guide](import-guide.md).

## Conduct a review

Use the **Reviews** area to send topics for review, track responses, and incorporate feedback. Reviewers can use an account or, when enabled, a private time-limited review link. Available actions depend on the review status and your role.

### Send a topic for review

From the Author area, choose **Send for Review** and select the topic and reviewer or reviewers. Set the due date and priority where offered, and add an optional message. If reviewers must act in order, use sequential review setup and arrange the sequence before sending.

### Incorporate review feedback

Open **Reviews > Incorporate Feedback** or choose **Incorporate** on an eligible review. Read the reviewer's feedback, update the topic, and save the changes. When the workflow requires another review, submit the revised topic again.

### View review history

Open **Reviews > History** to find completed reviews. Search or filter the list to locate a topic or reviewer, then open a review to inspect its details and feedback.

### View Review Tasks

Open **Reviews > Tasks** to see assigned review work. Use **My Reviews** for pending or in-progress assignments and **Completed** for finished reviews. Open a review to read the topic and submit feedback or a recommendation.

See the [Review Workflow Guide](REVIEW_WORKFLOW_GUIDE.md) for additional workflow details.

## Using administrative features

The following pages and actions require an administrator account. Open **Admin** to access the dashboard and administrative tools; some items appear as quick actions or in the Admin navigation.

### Manage users

From **Admin**, choose **Manage Users** to review accounts and manage user roles or access. Assign only the permissions each person needs.

### Create a notification

From the Admin dashboard, choose **Create Notification**. Enter the notification details and audience or delivery options shown, then submit it.

### Manage notifications

Choose **Manage Notifications** from the Admin dashboard to review existing notifications and use the available edit or management actions.

### Manage variables

Open **Admin > Variables** to create or edit variables used in topic content and publication-time configuration. Insert available variables from the topic editor; configure unresolved values for a collection before publishing when prompted.

### View Bug Reports

Open **Admin > Bugs** or choose **View Bug Reports** on the Admin dashboard. Review submitted reports and use the available actions to manage them.

### View the audit log

Open **Admin > Audit Log** to review the recorded create, update, and delete activity. The audit log is intended for viewing activity, not editing it.

### Find and replace text

Open **Admin > Find & Replace** to search and replace text across editable content. Review the matches and replacement scope carefully before applying a change.

### View system limits

On the Admin dashboard, choose **System Limits** to view or configure available upload-size and rate limits. These settings affect the application for other users too.

### Export branding

Open **Admin > Export Branding** to configure logos and styling used by PDF and HTML publication exports. Use the provided export test controls to check the branding against an existing publication.

### View Help Links

Open **Admin > Help Links** to manage contextual help destinations shown by help icons in the application.

### Viewing feedback

Open **Admin > Feedback** to review feedback submitted through the application. Use the available actions to manage or archive submissions.

### Viewing the Icon Catalog

Open **Admin > Icon Catalog** to browse the application's icon reference. This is a design reference, not a content-authoring tool.

### Viewing the Button Catalog

Open **Admin > Button Catalog** to browse examples of application buttons and their usage. This is a design reference, not a content-authoring tool.

## Publish a collection

Open **Collections > Publish** to manage publication snapshots made from collection content. Before exporting, check the content and audience tags. Refresh a publication after source topics change so the export includes the latest saved content.

### Publish a knowledge base

Create or open a publication for the collection, save its snapshot, and open the publication dashboard. Choose **Export KB** for the publication, or use the mobile knowledge-base page to preview, refresh, and download a knowledge base. Audience tags control which tagged snippets are included.

### Publish a PDF document

From the publication dashboard, choose **Export PDF** for a publication. You can also use **Save & Export PDF** from a collection's organize page where available. Preview or refresh the publication first if its source topics have changed.

### Manage publications

In **Collections > Publish**, use the publication list to preview, edit, refresh, or export a publication as a knowledge base or PDF. A saved snapshot represents the content selected at that time; refresh it to pull in later topic changes. Available exports depend on the installation.

## View metrics

Metrics summarize the work in the current area. Some pages also provide a calendar panel.

### View Home dashboard

Open **Home** to see an overview of projects, collections, topics, reviews, pending actions, and recent activity. Select a metric or quick action to open the related area when a link is available.

### Open page metrics

On a page that has a bar-chart button labeled **View Key Metrics**, select the button to open that page's metrics panel. The metrics are specific to the current page; close the panel to return to your work.

## Typical workflow

The exact sequence depends on your team, but this is a common path from project setup to reviewed content:

### Create a project (workflow step)

Use **Projects > Create Project** to enter the project name, status, and optional description.

### Add stakeholders to the project

During setup, add existing stakeholders with project roles or create new stakeholders. You can also complete this step later.

### Add milestones to the project

Add milestone names, dates, and statuses during setup or from **Projects > Milestones**.

### Create a collection (workflow step)

Create a collection under the project and give it a unique Collection ID, or create one by importing a document or multiple files.

### Add topics to the collection

Create topics in the Author area or import them, then organize the collection's topic membership and order.

### Send topics for review

Submit draft topics to the appropriate reviewers and provide due dates or instructions as needed.

### Incorporate changes

Read the feedback, update and save the topics, then resubmit them for review if required by your workflow.

## Related documentation

- [Import Guide](import-guide.md)
- [Review Workflow Guide](REVIEW_WORKFLOW_GUIDE.md)
- [Documentation Hub](README.md)
