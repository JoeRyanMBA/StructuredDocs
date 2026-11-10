# Review Workflow Guide

This guide explains how to submit topics for review and how review status moves through the app.

## Standard Review Flow

1. Go to **Author Dashboard** and find your draft topic.
2. Click **Submit for Review**.
3. In the modal, select:
   - Reviewer
   - Priority
   - Due days
   - Optional message
4. Click **Request Review**.
5. Topic status updates to **Pending Review** and review records appear in the Reviews area.

## Sequential Review Flow

Use sequential review when you want reviewers to work in order.

1. Click **Sequential review setup** on a draft topic.
2. Add reviewers in order (expert reviewer first).
3. Add optional step names/instructions.
4. Start sequence.
5. First reviewer is assigned; later steps proceed in sequence.

## Review Status Meanings

- `draft`: Authoring in progress, not yet submitted.
- `pending_review`: Submitted and waiting for reviewer action.
- `in_progress`: Reviewer has started working.
- `completed`: Review finished.
- `revisions_requested`: Author should update content and resubmit.
- `approved`: Review accepted.

## Bulk Review Content Edits

1. In the bulk review portal, select **Edit Content** and make your changes.
2. Select **Approve with minor changes**, then **Send & Continue** to submit
   the edited version with your feedback. Typing alone does not save to the
   server; do not refresh or close the page before submitting.
3. The author opens **View** on the completed review to reach **Incorporate
   Feedback**. The **Content Edits** section shows proposed changes for the
   author to accept or reject.

Reviewer edits do not automatically replace the topic. **Open in editor**
shows the existing topic until the author applies changes. A **Review
Completed** status confirms submission, not incorporation into the topic.

## Where to Manage Reviews

- **Reviews Dashboard**: high-level metrics and activity.
- **Reviews > Tasks**: review work queue.
- **Reviews > History**: completed reviews and past activity.
- **Incorporate Feedback**: apply reviewer comments to topics.

## Troubleshooting

- If **Submit for Review** succeeds but topic doesn’t appear in review lists, refresh Topics and Reviews pages.
- If creating a sequential review fails, verify reviewers are valid stakeholders with review capability.
- If reviewers are missing, check `/api/reviews/reviewers` availability and stakeholder setup.
