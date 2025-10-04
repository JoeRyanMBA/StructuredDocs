# Manual User Acceptance Testing (UAT) Checklist

This checklist is designed to help you systematically test the StructuredDocs application before releasing it to a wider audience for UAT.

## 1. Authentication

| Test Case ID | Feature | Action | Expected Result | Actual Result (Pass/Fail) | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |

| AUTH-01 | Login | Attempt to log in with valid credentials (`admin@example.com`, `ChangeMe123!`). | User is successfully logged in and redirected to the dashboard. | | |
| AUTH-02 | Login | Attempt to log in with an invalid username. | An appropriate error message is displayed. User is not logged in. | | |
| AUTH-03 | Login | Attempt to log in with a valid username and invalid password. | An appropriate error message is displayed. User is not logged in. | | |
| AUTH-04 | Login | Attempt to log in with empty credentials. | Validation messages appear for both fields. | | |
| AUTH-05 | Logout | Log in, then click the logout button. | User is successfully logged out and redirected to the login page. | | |
| AUTH-06 | Session | After logging in, refresh the page. | User remains logged in. | | |
| AUTH-07 | Access Control | After logging out, try to access a protected page (e.g., `/`) by manually entering the URL. | User is redirected to the login page. | | |

## 2. Main Navigation & Layout

| Test Case ID | Feature | Action | Expected Result | Actual Result (Pass/Fail) | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |

| NAV-01 | Header | Verify that the main header/navigation bar is present on all pages after login. | The header is consistently displayed. | | |
| NAV-02 | Navigation Links | Click on each main navigation link (Start, Projects, Tasks, etc.). | Each link navigates to the correct page without errors. The correct page content is displayed. | | |
| NAV-03 | Active Link | As you navigate, check if the currently active page is highlighted in the navigation bar. | The active link has a distinct style. | | |
| NAV-04 | Responsive Design | Resize the browser window to a mobile width. | The layout adjusts gracefully. No content is cut off or overlapping. A mobile menu (hamburger icon) may appear. | | |
| NAV-05 | Breadcrumbs | Navigate to a nested page (e.g., a specific project). | Breadcrumb navigation is displayed correctly and allows for easy navigation back to parent pages. | | |

## 3. Core Functionality (Projects, Tasks, etc.)

This section should be expanded based on the specific features of your application.

| Test Case ID | Feature | Action | Expected Result | Actual Result (Pass/Fail) | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |

| PROJ-01 | View Projects | Navigate to the Projects page. | A list of projects is displayed. | | |
| PROJ-02 | Create Project | Find and click the "Create Project" or similar button. Fill out the form and submit. | The new project is created and appears in the project list. A success message is shown. | | |
| PROJ-03 | Create Project | Attempt to create a project with invalid or missing data. | Validation errors are displayed, and the project is not created. | | |
| TASK-01 | View Tasks | Navigate to the Tasks page. | A list of tasks is displayed. | | |
| TASK-02 | Create Task | Find and click the "Create Task" or similar button. Fill out the form and submit. | The new task is created and appears in the task list. | | |
| ... | ... | ... | ... | ... | ... |

## 4. Forms and Data Entry

| Test Case ID | Feature | Action | Expected Result | Actual Result (Pass/Fail) | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |

| FORM-01 | Input Fields | For any form, enter valid data into all fields. | All data is accepted. | | |
| FORM-02 | Input Fields | Enter invalid data (e.g., text in a number field, incorrect email format). | Validation messages are shown for the specific fields. | | |
| FORM-03 | Required Fields | Attempt to submit a form with required fields left blank. | Validation messages highlight the required fields. The form is not submitted. | | |
| FORM-04 | Buttons | Verify that `Submit`, `Save`, and `Cancel` buttons work as expected on all forms. | Submit/Save saves the data. Cancel discards changes and closes the form/modal. | | |

## 5. General Usability and UI

| Test Case ID | Feature | Action | Expected Result | Actual Result (Pass/Fail) | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |

| UI-01 | Consistency | Check for consistent use of colors, fonts, and button styles across the application. | The UI is visually consistent. | | |
| UI-02 | Readability | Ensure all text is legible and has sufficient contrast. | All text is easy to read. | | |
| UI-03 | Error Messages | Intentionally perform actions that should cause errors. | Error messages are clear, user-friendly, and displayed in a consistent location. | | |
| UI-04 | Loading States | For actions that take time (e.g., fetching data), check for loading indicators (spinners, etc.). | Loading indicators are shown, preventing the user from clicking multiple times. | | |
| UI-05 | Empty States | View pages that have no data yet (e.g., a new user's project list). | A helpful "empty state" message is displayed instead of a blank page. | | |
| UI-06 | Broken Links | Click every link and button. | No links or buttons are broken or lead to error pages (404s). | | |

---
