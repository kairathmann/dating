import { List, Record } from 'immutable'
import { ASYNC_STATES } from 'src/enums'
import { LOAD_CONVERSATIONS_ERROR, LOAD_CONVERSATIONS_START, LOAD_CONVERSATIONS_SUCCESS, } from './action-types'

export const Conversations = new Record({
  list: new List(),
  fetchState: ASYNC_STATES.BEFORE,
})

export function conversationReducer (state = new Conversations(), { payload, type }) {
  switch (type) {
    case LOAD_CONVERSATIONS_START:
      return state.set('fetchState', ASYNC_STATES.DURING)

    case LOAD_CONVERSATIONS_ERROR:
      return state.merge({
        list: state.list.clear(),
        fetchState: ASYNC_STATES.FAIL
      })

    case LOAD_CONVERSATIONS_SUCCESS:
      return state.merge({
        list: new List(payload),
        fetchState: ASYNC_STATES.BEFORE
      })

    default:
      return state
  }
}
