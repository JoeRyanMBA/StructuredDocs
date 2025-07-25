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
