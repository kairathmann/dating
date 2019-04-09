import { List, Record } from 'immutable'
import { SIGN_OUT_SUCCESS } from 'src/auth/action-types'
import { ASYNC_STATES } from 'src/enums'

import {
  LOAD_MESSAGES_ERROR,
  LOAD_MESSAGES_START,
  LOAD_MESSAGES_SUCCESS,
  SEND_MESSAGE_BEFORE,
  SEND_MESSAGE_ERROR,
  SEND_MESSAGE_SUCCESS,
  SEND_MESSAGE_TRYING,
  UNLOAD_MESSAGES_SUCCESS,
  UPDATE_MESSAGES_SUCCESS,
} from './action-types'

export const MessagesState = new Record({
  list: new List(),
  fetchState: ASYNC_STATES.BEFORE,
  selectedConversation: null,
  sendState: ASYNC_STATES.BEFORE,
})

export function messagesReducer (state = new MessagesState(), { payload, type }) {
  switch (type) {

    case LOAD_MESSAGES_START:
      return state.merge({
        fetchState: ASYNC_STATES.DURING,
      })

    case LOAD_MESSAGES_ERROR:
      return state.merge({
        list: state.list.clear(),
        selectedConversation: null,
        fetchState: ASYNC_STATES.FAIL
      })

    case LOAD_MESSAGES_SUCCESS:
      const { conversation, messages } = payload
      return state.merge({
        selectedConversation: conversation,
        list: List(messages),
        fetchState: ASYNC_STATES.BEFORE
      })

    case UNLOAD_MESSAGES_SUCCESS:
      return state.set('list', new List())

    case UPDATE_MESSAGES_SUCCESS:
      return state.merge({
        list: state.list.map(messages => {
          return messages.id === payload.id ? payload : messages
        }),
      })

    case SIGN_OUT_SUCCESS:
      return new MessagesState()

    case SEND_MESSAGE_BEFORE:
      return state.set('sendState', ASYNC_STATES.BEFORE)
    case SEND_MESSAGE_TRYING:
      return state.set('sendState', ASYNC_STATES.DURING)
    case SEND_MESSAGE_SUCCESS:
      return state.set('sendState', ASYNC_STATES.SUCCESS)
    case SEND_MESSAGE_ERROR:
      return state.set('sendState', ASYNC_STATES.FAIL)

    default:
      return state
  }
}
