import { toAction } from 'src/common/utils'
import api from 'src/api'
import { decorateConversation, decorateMessage } from '../common/decorators'

import {
  CREATE_MESSAGES_ERROR,
  LOAD_MESSAGES_ERROR,
  LOAD_MESSAGES_START,
  LOAD_MESSAGES_SUCCESS,
  SEND_MESSAGE_BEFORE,
  SEND_MESSAGE_ERROR,
  SEND_MESSAGE_TRYING,
  UNLOAD_MESSAGES_SUCCESS,
  UPDATE_MESSAGES_ERROR,
  UPDATE_MESSAGES_SUCCESS,
} from './action-types'

export function createMessagesError (error) {
  return {
    type: CREATE_MESSAGES_ERROR,
    payload: error,
  }
}

export function updateMessagesError (error) {
  return {
    type: UPDATE_MESSAGES_ERROR,
    payload: error,
  }
}

export function updateMessagesSuccess (messages) {
  return {
    type: UPDATE_MESSAGES_SUCCESS,
    payload: messages,
  }
}

export function loadMessagesSuccess (messages) {
  return {
    type: LOAD_MESSAGES_SUCCESS,
    payload: messages,
  }
}

export function loadMessages (targetHid, conversationId) {

  return async dispatch => {
    dispatch(toAction(LOAD_MESSAGES_START))

    try {
      const resp = await api.fetchMessages({ target_hid: targetHid, conversation_id: conversationId })
      let { conversation, messages, ...rest } = resp.data.data

      const messagesFromApi = {
        ...rest,
        conversation: decorateConversation(conversation),
        messages: messages.map(decorateMessage)
      }

      dispatch(toAction(LOAD_MESSAGES_SUCCESS, messagesFromApi))
      return
    } catch (err) {
      dispatch(toAction(LOAD_MESSAGES_ERROR))
      return
    }
  }
}

export function unloadMessages () {
  // TODO
  return {
    type: UNLOAD_MESSAGES_SUCCESS,
  }
}

export function sendMessage (messageParams) {
  return async dispatch => {
    dispatch(toAction(SEND_MESSAGE_TRYING))

    try {
      const resp = await api.sendMessage({ recipient_hid: messageParams.targetUser, body: messageParams.body })

      const respData = resp.data.data
      const { viewerHid, conversationId } = respData

      await loadMessages(viewerHid, conversationId)(dispatch) // load immediately for seeing the new message
      dispatch(toAction(SEND_MESSAGE_BEFORE)) // if success - return to normal
      return
    } catch (err) {
      dispatch(toAction(SEND_MESSAGE_ERROR, err))

      setTimeout(() => {
        dispatch(toAction(SEND_MESSAGE_BEFORE))
      }, 2000) // return to normal after failure msg
    }

  }
}
