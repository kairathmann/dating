/* eslint no-throw-literal: 0 */
import { List } from 'immutable'
import { ASYNC_STATES } from '../enums'
import { LOAD_CONVERSATIONS_ERROR, LOAD_CONVERSATIONS_START, LOAD_CONVERSATIONS_SUCCESS } from './action-types'
import {conversationReducer,  Conversations } from './reducer'

describe('REDUCER', () => {

  it(`LOAD_CONVERSATIONS_START should set fetchState as DURING`, () => {
    const nextState = conversationReducer(new Conversations(), { type: LOAD_CONVERSATIONS_START, payload: null })
    expect(nextState.get('fetchState')).toEqual(ASYNC_STATES.DURING)
  })

  it(`LOAD_CONVERSATIONS_ERROR should set fetchState as FAIL and clean list`, () => {
    const nextState = conversationReducer(new Conversations(), { type: LOAD_CONVERSATIONS_ERROR, payload: null })
    expect(nextState.get('fetchState')).toEqual(ASYNC_STATES.FAIL)
    expect(nextState.get('list')).toEqual(new List())
  })

  it(`LOAD_CONVERSATIONS_SUCCESS should set fetchState as BEFORE and fill list`, () => {
    const nextState = conversationReducer(new Conversations(),
      { type: LOAD_CONVERSATIONS_SUCCESS, payload: [ { id: 1, partnerGender: 1 } ] })
    expect(nextState.get('fetchState')).toEqual(ASYNC_STATES.BEFORE)
    expect(nextState.get('list')).toEqual(new List([{ id: 1, partnerGender: 1 }]))
  })
})
