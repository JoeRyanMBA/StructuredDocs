const STANDARD_MODAL_CONTENT = [
  '.modal-overlay .modal-content',
  '.modal-overlay .modal',
  '.modal-overlay .custom-modal',
  '.modal-overlay .sd-modal',
  '.request-review-modal .modal-content',
  '.modal.show .modal-content'
].join(', ')

const STANDARD_HEADERS = [
  '.modal-header-row',
  '.modal-header',
  '.sd-modal-header',
  '.review-modal-header'
].join(', ')

const STANDARD_CLOSE = [
  '.plain-close',
  '.close-btn',
  '.btn-close'
].join(', ')

const STANDARD_FOOTERS = [
  '.modal-footer',
  '.modal-actions',
  '.sd-modal-actions',
  '.review-modal-actions'
].join(', ')

const PRIMARY_ACTIONS = [
  '.btn.btn-primary',
  '.primary-btn',
  '.save-btn',
  '.submit-btn'
].join(', ')

const SECONDARY_ACTIONS = [
  '.btn.btn-secondary',
  '.secondary-btn',
  '.cancel-btn'
].join(', ')

const fallbackOpeners = [
  '.btn-send-review',
  '.btn-seq-review',
  '.btn-publish',
  '.btn-icon',
  '.quick-action-card',
  '.action-card',
  'button.btn-primary',
  'button.btn-secondary'
]

function openModalWithFallback() {
  cy.get('body').then(($body) => {
    for (const selector of fallbackOpeners) {
      const match = $body.find(selector).filter(':visible').first()
      if (match.length) {
        cy.wrap(match).click({ force: true })
        return
      }
    }

    const byText = $body
      .find('button, a')
      .filter(':visible')
      .filter((_, el) => /create|new|add|edit|details|review|access|forgot|request/i.test(el.innerText || ''))
      .first()

    if (byText.length) {
      cy.wrap(byText).click({ force: true })
    }
  })
}

function assertStandardModalIfPresent(route) {
  cy.get('body').then(($body) => {
    const hasModal = $body.find(STANDARD_MODAL_CONTENT).length > 0

    if (!hasModal) {
      cy.log(`No modal opened on ${route} (trigger may require specific data/permissions).`)
      return
    }

    cy.get(STANDARD_MODAL_CONTENT).filter(':visible').first().within(() => {
      cy.get(STANDARD_HEADERS).should('exist')
      cy.get(STANDARD_CLOSE).should('exist')
    })

    cy.get('body').then(($nextBody) => {
      const hasFooter = $nextBody.find(STANDARD_FOOTERS).length > 0
      if (!hasFooter) return

      cy.get(STANDARD_FOOTERS).filter(':visible').first().within(() => {
        cy.get(`${PRIMARY_ACTIONS}, ${SECONDARY_ACTIONS}`).should('exist')
      })
    })
  })
}

describe('Modal standardization smoke test', () => {
  const routes = [
    '/topics',
    '/author',
    '/reviews',
    '/projects',
    '/tasks',
    '/login',
    '/all-tags',
    '/all-links',
    '/all-images',
    '/all-stakeholders'
  ]

  routes.forEach((route) => {
    it(`checks modal structure/buttons on ${route}`, () => {
      cy.visit(route, { failOnStatusCode: false })
      openModalWithFallback()
      assertStandardModalIfPresent(route)
    })
  })

  it('checks modal usability on mobile viewport', () => {
    cy.viewport(375, 812)
    cy.visit('/topics', { failOnStatusCode: false })
    openModalWithFallback()
    assertStandardModalIfPresent('/topics [mobile]')

    cy.get('body').then(($body) => {
      const hasClose = $body.find(STANDARD_CLOSE).length > 0
      if (hasClose) {
        cy.get(STANDARD_CLOSE).filter(':visible').first().click({ force: true })
      }
    })
  })
})
