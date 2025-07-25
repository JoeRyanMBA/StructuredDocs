# drag-event-service
Register both mouse and touch event.
```js
// mapping
const events = {
  start: ['mousedown', 'touchstart'],
  move: ['mousemove', 'touchmove'],
  end: ['mouseup', 'touchend'],
}
```
# install
```sh
npm install drag-event-service
```
# usage & api
```js
import DragEventService from 'drag-event-service'
DragEventService.on(el, name, handler, ...other args)
```
## on(el, name, handler, ...args); off(el, name, handler, ...args)
* The args will pass to addEventListener.
* The second argument of handler is current position({x, y}).

# example
```js
DragEventService.on(document, 'move', (e, mouse) => ..., {passive: false})
```
