import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'
import { compileTemplate, parse } from '@vue/compiler-sfc'

const imagePickerComponents = [
  '../src/components/TopicEditor.vue',
  '../src/views/SnippetsLibrary.vue',
]

for (const componentPath of imagePickerComponents) {
  test(`${componentPath} compiles an optional preview for the selected uploaded image`, async () => {
    const source = await readFile(new URL(componentPath, import.meta.url), 'utf8')
    const { descriptor, errors: parseErrors } = parse(source, { filename: componentPath })
    assert.deepEqual(parseErrors, [])

    const { errors: templateErrors } = compileTemplate({
      source: descriptor.template.content,
      filename: componentPath,
      id: 'insert-image-preview-test',
    })
    assert.deepEqual(templateErrors, [])
    assert.match(descriptor.template.content, /Preview selected image/)
    assert.match(descriptor.template.content, /:disabled="!selectedExistingImage"/)
    assert.match(descriptor.template.content, /imagePreviewVisible && selectedExistingImage/)
    assert.match(descriptor.template.content, /imageDisplayUrl\(selectedExistingImage\)/)
  })
}
