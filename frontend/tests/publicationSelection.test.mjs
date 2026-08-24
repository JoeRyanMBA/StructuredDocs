import assert from 'node:assert/strict'
import test from 'node:test'

const { resolveSelectedPublicationId } = await import('../src/utils/publicationSelection.js')

test('auto-selects the only filtered publication when nothing is selected', () => {
  const publications = [{ id: 5, title: 'Test Collection 4' }]

  assert.equal(resolveSelectedPublicationId('', publications, ''), '5')
})

test('keeps the current valid selection when it still matches the filtered results', () => {
  const publications = [
    { id: 3, title: 'Alpha' },
    { id: 5, title: 'Beta' },
  ]

  assert.equal(resolveSelectedPublicationId('5', publications, ''), '5')
})

test('clears the selection when the filtered set has multiple matches and no current selection is valid', () => {
  const publications = [
    { id: 3, title: 'Alpha' },
    { id: 5, title: 'Beta' },
  ]

  assert.equal(resolveSelectedPublicationId('', publications, 'a'), '')
})
