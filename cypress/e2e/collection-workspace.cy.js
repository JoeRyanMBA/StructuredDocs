describe('Collection workspace', () => {
  const reference = '<div class="sd-snippet-ref" data-snippet-id="10">Snippet placeholder</div>'
  let topics

  beforeEach(() => {
    topics = {
      1: { id: 1, title: 'Getting started', content: `## Welcome to {{product}}\n\n${'Complete topic content. '.repeat(20)}\n\n${reference}`, frontmatter: '' },
      2: { id: 2, title: 'Nested procedure', content: 'The nested procedure body.', frontmatter: '' },
    }
    cy.intercept('GET', '/api/collections', [{ id: 5, name: 'Field Guide', children: [] }])
    cy.intercept('GET', '/api/collections/5', {
      id: 5, name: 'Field Guide', topics: [{ id: 1, title: 'Getting started', children: [{ id: 2, title: 'Nested procedure', children: [] }] }],
    })
    cy.intercept('PUT', '/api/collections', { success: true }).as('saveCollection')
    cy.intercept('POST', '/api/collections/5/publish', { id: 20 }).as('publish')
    cy.intercept('GET', '/api/topics', { topics: Object.values(topics) })
    cy.intercept('GET', '/api/topics/usage-summary', {
      1: { collections: [{ id: 5, name: 'Field Guide' }, { id: 6, name: 'Office Guide' }] },
      2: { collections: [{ id: 5, name: 'Field Guide' }] },
    })
    cy.intercept('GET', '/api/topics/[12]', req => req.reply(topics[req.url.split('/').pop()]))
    cy.intercept('PUT', '/api/topics/[12]', req => {
      const topicId = req.url.split('/').pop()
      topics[topicId] = { ...topics[topicId], ...req.body }
      req.reply(topics[topicId])
    }).as('saveTopic')
    cy.intercept('GET', '/api/tags/', [{ id: 7, name: 'Field staff' }])
    cy.intercept('POST', '/api/variables/collections/5/preview', { mapping: { product: 'Widget' } })
    cy.intercept('GET', '/api/snippets/10', { id: 10, content: 'Field-specific snippet.', tags: [{ id: 7 }] })
    cy.visit('/organize/5', {
      onBeforeLoad(window) {
        window.localStorage.clear()
        window.localStorage.setItem('user', JSON.stringify({ id: 1, username: 'Tester', role: 'admin' }))
        window.localStorage.setItem('access_token', 'test.test.test')
      },
    })
    cy.get('.collection-html-preview').should('contain', 'Welcome to Widget')
  })

  it('previews full content, filters tagged snippets, and navigates nested topics', () => {
    cy.viewport(1440, 1000)
    cy.get('.collection-html-content').invoke('text').should('have.length.greaterThan', 200)
    cy.get('.collection-html-content').should('not.contain', 'Field-specific snippet')
    cy.get('.shared-topic-warning').should('contain', '2 collections')
    cy.get('.shared-topic-warning summary').click()
    cy.get('.shared-topic-warning').should('contain', 'Office Guide')
    cy.get('.audience-settings summary').click()
    cy.contains('.audience-options label', 'Field staff').find('input').check()
    cy.get('.collection-html-content').should('contain', 'Field-specific snippet')
    cy.get('.expand-toggle').first().click()
    cy.contains('.collections-panel .topic-title', 'Nested procedure').click()
    cy.get('.collection-html-preview').should('contain', 'The nested procedure body.')
    cy.location('search').should('contain', 'topic=2')
    cy.get('.shared-topic-warning').should('not.exist')
    cy.screenshot('collection-workspace-desktop')
  })

  it('protects edits when changing topics and returns to preview after saving', () => {
    cy.get('.reader-tabs').contains('button', 'Edit').click()
    cy.get('.shared-topic-warning').should('contain', 'Changes affect all of them')
    cy.get('.editor-mode-toggle').contains('button', 'Markdown').click()
    cy.get('.markdown-editor textarea').clear().type('Updated collection topic.')
    cy.get('.expand-toggle').first().click()
    cy.contains('.collections-panel .topic-title', 'Nested procedure').click()
    cy.get('.unsaved-topic-dialog').should('be.visible').contains('button', 'Cancel').click()
    cy.get('.markdown-editor textarea').should('have.value', 'Updated collection topic.')
    cy.contains('.collections-panel .topic-title', 'Nested procedure').click()
    cy.get('.unsaved-topic-dialog').contains('button', 'Save').click()
    cy.wait('@saveTopic')
    cy.get('.collection-html-preview').should('contain', 'The nested procedure body.')
    cy.contains('.collections-panel .topic-title', 'Getting started').click()
    cy.get('.collection-html-preview').should('contain', 'Updated collection topic.')
    cy.get('.reader-tabs').contains('button', 'Edit').click()
    cy.get('.editor-mode-toggle').contains('button', 'Markdown').click()
    cy.get('.markdown-editor textarea').clear().type('Discard this draft.')
    cy.get('.reader-tabs').contains('button', 'Preview').click()
    cy.get('.unsaved-topic-dialog').contains('button', 'Discard').click()
    cy.get('.collection-html-preview').should('contain', 'Updated collection topic.').and('not.contain', 'Discard this draft.')
  })

  it('keeps the outline usable on mobile without horizontal overflow', () => {
    cy.viewport(390, 844)
    cy.get('.collections-panel').should('not.be.visible')
    cy.contains('button', 'Outline').click()
    cy.get('.collections-panel').should('be.visible')
    cy.get('.expand-toggle').first().click()
    cy.contains('.collections-panel .topic-title', 'Nested procedure').click()
    cy.get('.collection-html-preview').should('contain', 'The nested procedure body.')
    cy.get('.collections-panel').should('not.be.visible')
    cy.document().then(document => {
      expect(document.documentElement.scrollWidth).to.be.at.most(390)
    })
    cy.screenshot('collection-workspace-mobile')
  })

  it('passes the selected audience tags to HTML export', () => {
    cy.get('.audience-settings summary').click()
    cy.contains('.audience-options label', 'Field staff').find('input').check()
    cy.contains('button', 'Save & Export HTML').click()
    cy.wait('@saveCollection')
    cy.wait('@publish')
    cy.location('search').should('contain', 'tag_ids=7')
    cy.get('.audience-bar input').should('be.checked')
  })
})