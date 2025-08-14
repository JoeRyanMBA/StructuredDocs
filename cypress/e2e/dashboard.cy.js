describe('StructuredDocs Dashboard E2E', () => {
  before(() => {
    // Log in as admin before all tests
    cy.visit('/login');
    cy.get('input#email').type('admin@example.com');
    cy.get('input#password').type('admin123');
    cy.get('button.login-btn').click();
    // Wait for redirect to dashboard or projects
    cy.url().should('not.include', '/login');
  });

  it('Loads the dashboard and displays the Projects panel', () => {
    cy.visit('/projects');
    cy.contains('Projects Dashboard').should('exist');
  });

  it('Can add a new project and see it in the list', () => {
    cy.visit('/projects');
    // Wait for dashboard to load and button to be visible
  cy.get('button.action-card').contains('Create Project').should('be.visible').click();
  cy.get('input[placeholder="Enter project name"]').should('be.visible').type('E2E Test Project');
  cy.get('textarea[placeholder="Project description"]').type('This is a test project created by Cypress.');
  cy.get('button.create-btn').contains('Create Project').click();
  // Wait for modal to close and new project to appear
  cy.contains('E2E Test Project', { timeout: 10000 }).should('exist');
  });

  // Add more tests for stakeholders, milestones, collections, etc.
});
