# vue-functions
# install
```sh
npm install vue-functions
```
# usage & api
```js
import * as vf from 'vue-functions'
vf.method(...)
```
# api
### updatablePropsEvenUnbound
```js
// eg 1
export default {
  mixins: [vf.updatablePropsEvenUnbound({
    value: {localName: 'current'},
  })],
}
// eg 2
// if without localName, the localName will be 'localProps_' + prop name
export default {
  mixins: [vf.updatablePropsEvenUnbound({
    value: {},
  })],
}
// eg 3
// if without localName, the localName will be 'localProps_' + prop name
export default {
  mixins: [vf.updatablePropsEvenUnbound({
    value: {},
    page: {},
    other: {},
  })],
}
```
### watchAsync(vm, getter, handler, opt)
Watch a function and resolve dependences. The function can contain async dependences. There is no more doc, please check source.

### doWatch(vm, handler)
do handler first, handler return getter

### * iterateObjectWithoutDollarDash(obj)
Like name

### windowSize
Vue component, extend or mixin it to use. Get access to windowSize. The windowSize is reactive.
```js
windowSize: {
  innerWidth: window.innerWidth,
  innerHeight: window.innerHeight,
  outerWidth: window.outerWidth,
  outerHeight: window.outerHeight,
}
```

### registerPreventURLChange(Vue, router, msg)
Attach `$preventURLChange` and `$allowURLChange` to vm.
