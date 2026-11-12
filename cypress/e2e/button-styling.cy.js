describe('Standard button styling', () => {
  beforeEach(() => {
    cy.visit('/')
    cy.readFile('frontend/node_modules/bootstrap/dist/css/bootstrap.min.css').then(bootstrap => {
      cy.readFile('frontend/src/assets/style.css').then(buttons => {
        cy.readFile('frontend/src/styles/modal.css').then(modal => {
          cy.readFile('frontend/src/style.css').then(layout => {
            cy.readFile('frontend/src/components/CollectionTopicPane.vue').then(component => {
              const footer = component.match(/<div class="modal-footer">([\s\S]*?)<\/div>/)
              expect(footer, 'unsaved changes footer').not.to.be.null
              cy.document().then(doc => {
                doc.head.querySelectorAll('style, link[rel="stylesheet"]').forEach(node => node.remove())
                const style = doc.createElement('style')
                style.textContent = [bootstrap, buttons, layout.replace(/@import[^;]+;/, modal)]
                  .join('\n')
                  .replaceAll(':hover', '.test-hover')
                  .replaceAll(':active', '.test-active')
                doc.head.appendChild(style)
                doc.body.innerHTML = `<div class="modal-footer">${footer[1]}</div>
                  <div class="modal-actions">
                    <button class="btn btn-primary">Confirm</button>
                    <button class="btn btn-secondary">Cancel</button>
                  </div>`
              })
            })
          })
        })
      })
    })
  })

  it('keeps unsaved-topic Save teal when hovered, pressed, or saving', () => {
    cy.contains('.modal-footer button', 'Save').as('save')
    cy.get('@save').should('have.css', 'background-color', 'rgb(0, 91, 110)')
    cy.get('@save').invoke('addClass', 'test-hover')
      .should('have.css', 'background-color', 'rgb(0, 140, 158)')
    cy.get('@save').invoke('addClass', 'test-active')
      .should('have.css', 'background-color', 'rgb(0, 91, 110)')
    cy.get('@save').invoke('prop', 'disabled', true)
      .should('have.css', 'background-color', 'rgb(0, 91, 110)')
    cy.get('@save').should('have.css', 'opacity', '0.6')
  })

  it('uses the same palette for both modal button class conventions', () => {
    cy.get('.modal-footer .secondary-btn, .modal-actions .btn-secondary')
      .should('have.css', 'background-color', 'rgb(233, 236, 239)')
    cy.get('.modal-footer .secondary-btn, .modal-actions .btn-secondary')
      .should('have.css', 'color', 'rgb(0, 91, 110)')
    cy.get('.modal-footer .secondary-btn, .modal-actions .btn-secondary')
      .invoke('addClass', 'test-hover')
      .should('have.css', 'background-color', 'rgb(72, 201, 176)')
    cy.get('.modal-footer .secondary-btn, .modal-actions .btn-secondary')
      .invoke('addClass', 'test-active')
      .should('have.css', 'background-color', 'rgb(233, 236, 239)')
    cy.get('.modal-actions .btn-primary')
      .should('have.css', 'background-color', 'rgb(0, 91, 110)')
      .invoke('addClass', 'test-active')
      .should('have.css', 'background-color', 'rgb(0, 91, 110)')
  })
})
