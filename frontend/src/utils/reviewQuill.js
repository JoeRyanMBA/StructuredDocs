import Quill from 'quill'

const Image = Quill.import('formats/image')
const imageAttributes = [
  'data-sd-image-alignment',
  'data-sd-image-wrapping',
  'data-sd-image-size',
]
const imageStyleProperties = [
  'width', 'height', 'max-width', 'display', 'float',
  'margin-left', 'margin-right', 'margin-top', 'margin-bottom',
  'position', 'z-index', 'top', 'left', 'opacity', 'transform', 'shape-outside',
]

class ReviewImage extends Image {
  static formats(node) {
    const formats = super.formats(node)
    for (const name of imageAttributes) {
      if (node.hasAttribute(name)) formats[name] = node.getAttribute(name)
    }
    const style = imageStyleProperties
      .filter(property => node.style.getPropertyValue(property))
      .map(property => `${property}: ${node.style.getPropertyValue(property)}`)
      .join('; ')
    if (style) formats['review-image-style'] = style
    return formats
  }

  format(name, value) {
    if (imageAttributes.includes(name)) {
      if (value) this.domNode.setAttribute(name, value)
      else this.domNode.removeAttribute(name)
    } else if (name === 'review-image-style') {
      if (value) this.domNode.setAttribute('style', value)
      else this.domNode.removeAttribute('style')
    } else {
      super.format(name, value)
    }
  }
}

Quill.register('formats/image', ReviewImage, true)

export default Quill
