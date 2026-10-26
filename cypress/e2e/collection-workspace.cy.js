describe('Collection workspace', () => {
  const reference = '<div class="sd-snippet-ref" data-snippet-id="10">Snippet placeholder</div>'
  let topics
  let collectionTopics
  let createdTopics
  let collectionSaveFailures
  let savedTree

  beforeEach(() => {
    topics = {
      1: { id: 1, title: 'Getting started', content: `## Welcome to {{product}}\n\n${'Complete topic content. '.repeat(20)}\n\n${reference}`, frontmatter: '' },
      2: { id: 2, title: 'Nested procedure', content: 'The nested procedure body.', frontmatter: '' },
    }
    collectionTopics = [{ id: 1, title: 'Getting started', children: [{ id: 2, title: 'Nested procedure', children: [] }] }]
    createdTopics = 0
    collectionSaveFailures = 0
    savedTree = null
    cy.intercept('GET', '/api/collections', [{ id: 5, name: 'Field Guide', children: [] }])
    cy.intercept('GET', '/api/collections/5', req => {
      req.reply({ id: 5, name: 'Field Guide', topics: collectionTopics })
    })
    cy.intercept('PUT', '/api/collections', req => {
      if (collectionSaveFailures > 0) {
        collectionSaveFailures--
        req.reply({ statusCode: 500, body: { error: 'Collection save failed' } })
        return
      }
      savedTree = req.body.find(collection => collection.id === 5).topics
      collectionTopics = savedTree
      req.reply({ success: true })
    }).as('saveCollection')
    cy.intercept('POST', '/api/collections/5/publish', { id: 20 }).as('publish')
    cy.intercept('GET', '/api/topics', { topics: Object.values(topics) })
    cy.intercept('GET', '/api/topics/usage-summary', {
      1: { collections: [{ id: 5, name: 'Field Guide' }, { id: 6, name: 'Office Guide' }] },
      2: { collections: [{ id: 5, name: 'Field Guide' }] },
    })
    cy.intercept('POST', '/api/topics/', req => {
      const topicId = 3 + createdTopics++
      topics[topicId] = { ...req.body, id: topicId }
      req.reply({ statusCode: 201, body: topics[topicId] })
    }).as('createTopic')
    cy.intercept('GET', '/api/topics/[0-9]*', req => req.reply(topics[req.url.split('/').pop()]))
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

  function fillDraft(title) {
    cy.get('.topic-editor #title').type(title)
    cy.get('.editor-mode-toggle').contains('button', 'Markdown').click()
    cy.get('.markdown-editor textarea').type('New topic body.')
  }

  it('separates collection and topic tools and creates a root topic at the end', () => {
    cy.get('.collection-tools').should('contain', 'Collection Tools').and('contain', 'Add Existing Topics')
    cy.get('.reader-toolbar').should('contain', 'Topic Tools')
    cy.get('.collection-tools').contains('button', 'New Topic').click()
    fillDraft('New root topic')
    cy.get('.reader-toolbar').contains('button', /^Save$/).click()
    cy.wait('@createTopic')
    cy.wait('@saveCollection')
    cy.get('.collection-html-preview').should('contain', 'New root topic')
    cy.then(() => expect(savedTree.map(topic => topic.id)).to.deep.equal([1, 3]))
  })

  it('creates a child beneath the selected topic', () => {
    cy.get('.reader-toolbar').contains('button', 'New Child Topic').click()
    cy.get('.draft-context').should('contain', 'Getting started')
    fillDraft('New child topic')
    cy.get('.reader-toolbar').contains('button', /^Save$/).click()
    cy.wait('@createTopic')
    cy.wait('@saveCollection')
    cy.get('.collection-html-preview').should('contain', 'New child topic')
    cy.then(() => expect(savedTree[0].children.map(topic => topic.id)).to.deep.equal([2, 3]))
  })

  it('creates the first topic from an empty collection and cancels drafts without saving', () => {
    collectionTopics = []
    cy.reload()
    cy.get('.reader-state').should('contain', 'No topics in this collection')
    cy.get('.reader-state').contains('button', 'New Topic').click()
    cy.get('.reader-toolbar').contains('button', /^Cancel$/).click()
    cy.get('.reader-state').should('contain', 'No topics in this collection')
    cy.then(() => expect(createdTopics).to.equal(0))
    cy.get('.reader-state').contains('button', 'New Topic').click()
    fillDraft('First topic')
    cy.get('.reader-toolbar').contains('button', /^Save$/).click()
    cy.wait('@createTopic')
    cy.wait('@saveCollection')
    cy.get('.collection-html-preview').should('contain', 'First topic')
    cy.then(() => expect(savedTree.map(topic => topic.id)).to.deep.equal([3]))
  })

  it('retries failed collection attachment without creating the topic twice', () => {
    collectionSaveFailures = 1
    cy.get('.collection-tools').contains('button', 'New Topic').click()
    fillDraft('Retained topic')
    cy.get('.reader-toolbar').contains('button', /^Save$/).click()
    cy.wait('@createTopic')
    cy.wait('@saveCollection').its('response.statusCode').should('equal', 500)
    cy.contains('[role="alert"]', 'was saved, but could not be added').should('be.visible')
    cy.contains('button', 'Retry Add to Collection').click()
    cy.wait('@saveCollection').its('response.statusCode').should('equal', 200)
    cy.get('.collection-html-preview').should('contain', 'Retained topic')
    cy.then(() => {
      expect(createdTopics).to.equal(1)
      expect(savedTree.filter(topic => topic.id === 3)).to.have.length(1)
    })
  })

  it('disables child creation at the nesting limit', () => {
    collectionTopics = [{ id: 1, title: 'Level 1', children: [{ id: 2, title: 'Level 2', children: [{ id: 3, title: 'Level 3', children: [{ id: 4, title: 'Level 4', children: [{ id: 5, title: 'Level 5', children: [] }] }] }] }] }]
    topics[5] = { id: 5, title: 'Level 5', content: 'Deepest topic.' }
    cy.reload()
    cy.contains('button', 'Expand All').click()
    cy.contains('.collections-panel .topic-title', 'Level 5').click()
    cy.get('.collection-html-preview').should('contain', 'Deepest topic.')
    cy.get('.reader-toolbar').contains('button', 'New Child Topic').should('be.disabled')
  })
})