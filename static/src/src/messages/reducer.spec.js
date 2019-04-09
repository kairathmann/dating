import Immutable, { List } from 'immutable'
import { SIGN_OUT_SUCCESS } from '../auth'
/* eslint no-throw-literal: 0 */
import { ASYNC_STATES } from '../enums'
import {
  LOAD_MESSAGES_ERROR,
  LOAD_MESSAGES_START,
  LOAD_MESSAGES_SUCCESS,
  SEND_MESSAGE_BEFORE,
  SEND_MESSAGE_ERROR,
  SEND_MESSAGE_SUCCESS,
  SEND_MESSAGE_TRYING,
  UNLOAD_MESSAGES_SUCCESS
} from './action-types'
import { messagesReducer, MessagesState } from './reducer'

describe('REDUCER', () => {

  it(`LOAD_MESSAGES_START should set fetchState as DURING`, () => {
    const nextState = messagesReducer(new MessagesState(), { type: LOAD_MESSAGES_START })
    expect(nextState.get('fetchState')).toEqual(ASYNC_STATES.DURING)
  })

  it(`LOAD_MESSAGES_ERROR should set fields`, () => {
    const nextState = messagesReducer(new MessagesState(),
      { type: LOAD_MESSAGES_ERROR })
    expect(nextState.get('fetchState')).toEqual(ASYNC_STATES.FAIL)
    expect(nextState.get('list')).toEqual(new List())
    expect(nextState.get('selectedConversation')).toEqual(null)
  })

  it(`LOAD_MESSAGES_SUCCESS should set messages and conversation`, () => {
    const nextState = messagesReducer(new MessagesState(),
      { type: LOAD_MESSAGES_SUCCESS, payload: { conversation: {}, messages: [] } })
    expect(nextState.get('list')).toEqual(new List([]))
    expect(nextState.get('selectedConversation')).toEqual(new Immutable.Map({}))
    expect(nextState.get('fetchState')).toEqual(ASYNC_STATES.BEFORE)
  })

  it(`UNLOAD_MESSAGES_SUCCESS should clear list`, () => {
    const nextState = messagesReducer(new MessagesState(),
      { type: UNLOAD_MESSAGES_SUCCESS })
    expect(nextState.get('list')).toEqual(new List())
  })

  it('SIGN_OUT_SUCCESS should clear state', () => {
    const nextState = messagesReducer(new MessagesState(), { type: SIGN_OUT_SUCCESS })
    expect(nextState).toEqual(new MessagesState())
  })

  it('SEND_MESSAGE_BEFORE should set sendState', () => {
    const nextState = messagesReducer(new MessagesState(),
      { type: SEND_MESSAGE_BEFORE })
    expect(nextState.get('sendState')).toEqual(ASYNC_STATES.BEFORE)
  })

  it('SEND_MESSAGE_TRYING should set sendState', () => {
    const nextState = messagesReducer(new MessagesState(),
      { type: SEND_MESSAGE_TRYING })
    expect(nextState.get('sendState')).toEqual(ASYNC_STATES.DURING)
  })

  it('SEND_MESSAGE_SUCCESS should set sendState', () => {
    const nextState = messagesReducer(new MessagesState(),
      { type: SEND_MESSAGE_SUCCESS })
    expect(nextState.get('sendState')).toEqual(ASYNC_STATES.SUCCESS)
  })

  it('SEND_MESSAGE_ERROR should set sendState', () => {
    const nextState = messagesReducer(new MessagesState(),
      { type: SEND_MESSAGE_ERROR })
    expect(nextState.get('sendState')).toEqual(ASYNC_STATES.FAIL)
  })

})
