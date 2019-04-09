import { toAction } from 'src/common/utils'
import api from 'src/api'
import { decorateConversation } from '../common/decorators'
import {
  LOAD_CONVERSATIONS_ERROR,
  LOAD_CONVERSATIONS_START,
  LOAD_CONVERSATIONS_SUCCESS,
  UNLOAD_CONVERSATIONS
} from './action-types'

export const unloadConversations = () => toAction(UNLOAD_CONVERSATIONS)

export function loadConversations (targetHid) {

  return async dispatch => {
    dispatch(toAction(LOAD_CONVERSATIONS_START))
    try {
      const resp = await api.fetchConversations({ 'target_hid': targetHid })
      const conversations = resp.data.data.conversations
      return dispatch(toAction(LOAD_CONVERSATIONS_SUCCESS, conversations.map(decorateConversation)))
    } catch (err) {
      dispatch(toAction(LOAD_CONVERSATIONS_ERROR))
    }
  }
}




