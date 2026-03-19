// Cypress support file for e2e tests

// Stub all API calls so a missing backend doesn't hang requests or affect page loading
beforeEach(() => {
  cy.intercept('/api/**', (req) => {
    req.reply({ statusCode: 200, body: [] })
  })
})
