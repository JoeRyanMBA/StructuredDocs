function setAdminSession(win) {
  win.localStorage.setItem('user', JSON.stringify({ id: 1, role: 'admin', name: 'Admin User' }))
}

describe('Notifications workflow smoke', () => {
  it('manages notifications list: load, toggle, delete', () => {
    let notifications = [
      {
        id: 101,
        title: 'Initial Notice',
        message: 'System maintenance tonight',
        type: 'global',
        is_active: true,
        target_audience: null,
        created_at: '2026-04-28T10:00:00Z',
      },
    ]

    cy.intercept('GET', '**/api/notifications?include_inactive=true', (req) => {
      req.reply({ statusCode: 200, body: notifications })
    }).as('getNotifications')

    cy.intercept('POST', '**/api/notifications/101/toggle', () => {
      notifications = notifications.map((n) => (n.id === 101 ? { ...n, is_active: !n.is_active } : n))
      return { statusCode: 200, body: notifications.find((n) => n.id === 101) }
    }).as('toggleNotification')

    cy.intercept('DELETE', '**/api/notifications/101', () => {
      notifications = notifications.filter((n) => n.id !== 101)
      return { statusCode: 200, body: { deleted: true } }
    }).as('deleteNotification')

    cy.visit('/notifications/manage', {
      failOnStatusCode: false,
      onBeforeLoad(win) {
        setAdminSession(win)
      },
    })

    cy.wait('@getNotifications')
    cy.contains('Notification Management').should('be.visible')
    cy.contains('System maintenance tonight').should('be.visible')

    cy.contains('button', 'Deactivate').click()
    cy.wait('@toggleNotification')
    cy.wait('@getNotifications')
    cy.contains('button', 'Activate').should('be.visible')

    cy.on('window:confirm', () => true)
    cy.contains('button', 'Delete').click()
    cy.wait('@deleteNotification')
    cy.wait('@getNotifications')
    cy.contains('No Notifications').should('be.visible')
  })

  it('creates a notification from the create page', () => {
    cy.intercept('POST', '**/api/notifications', (req) => {
      expect(req.body).to.include({
        title: 'Release Update',
        message: 'Version 2.1 deployed',
        type: 'admin',
      })
      req.reply({
        statusCode: 201,
        body: {
          id: 202,
          ...req.body,
          is_active: true,
          created_at: '2026-04-28T11:00:00Z',
        },
      })
    }).as('createNotification')

    cy.visit('/notifications/new', {
      failOnStatusCode: false,
      onBeforeLoad(win) {
        setAdminSession(win)
      },
    })

    cy.get('#title').clear().type('Release Update')
    cy.get('#message').clear().type('Version 2.1 deployed')
    cy.get('#type').select('admin')
    cy.contains('button', 'Create').click()

    cy.wait('@createNotification')
    cy.location('pathname').should('eq', '/admin')
  })

  it('edits an existing notification', () => {
    cy.intercept('GET', '**/api/notifications/303', {
      statusCode: 200,
      body: {
        id: 303,
        title: 'Old Title',
        message: 'Old message',
        type: 'global',
      },
    }).as('getNotification')

    cy.intercept('PUT', '**/api/notifications/303', (req) => {
      expect(req.body).to.include({
        title: 'Old Title',
        message: 'Updated message content',
        type: 'global',
      })
      req.reply({ statusCode: 200, body: { id: 303, ...req.body } })
    }).as('updateNotification')

    cy.visit('/notifications/edit/303', {
      failOnStatusCode: false,
      onBeforeLoad(win) {
        setAdminSession(win)
      },
    })

    cy.wait('@getNotification')
    cy.get('#message').clear().type('Updated message content')
    cy.contains('button', 'Save Changes').click()

    cy.wait('@updateNotification')
    cy.location('pathname').should('eq', '/admin')
  })
})
