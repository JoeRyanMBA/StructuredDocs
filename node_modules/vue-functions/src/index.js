import * as hp from 'helper-js'

export function updatablePropsEvenUnbound(props) {
  const component = {
    props,
    computed: {},
    watch: {},
  }
  let propNames
  const localNames = {}
  if (hp.isArray(props)) {
    propNames = props
  } else {
    propNames = []
    for (const key in props) {
      propNames.push(key)
      if (props[key].localName) {
        localNames[key] = props[key].localName
        delete props[key].localName
      }
    }
  }
  component.data = function () {
    const t = {
      localValueOfUpdatableProps: {},
    }
    for (const name of propNames) {
      t.localValueOfUpdatableProps[name] = this[name]
    }
    return t
  }
  for (const name of propNames) {
    component.watch[name] = function (value) {
      const ignore = `_ignoreOnce_${name}`
      if (this[ignore]) {
        this[ignore] = false
        return
      }
      this.localValueOfUpdatableProps[name] = value
    }
    const localName = localNames[name] || `localProps_${name}`
    component.computed[localName] = {
      get(){ return this.localValueOfUpdatableProps[name] },
      set(value) {
        const ignore = `_ignoreOnce_${name}`
        this[ignore] = true
        if (name === 'value') {
          this.$emit('input', value)
        } else {
          this.$emit(`update:${name}`, value)
        }
        this.localValueOfUpdatableProps[name] = value
      },
    }
  }
  return component
}

export function isPropTrue(value) {
  return value === '' || value
}
