import api from 'src/api'
import { initAuth, signInError } from 'src/auth/actions'

import { toAction } from 'src/common/utils'

import {
  LOAD_USER_ERROR,
  LOAD_USER_SUCCESS,
  LOAD_VIEW_USER,
  REMOVE_USER_SUCCESS,
  UNLOAD_USER_SUCCESS,
  UPDATE_USER_ERROR,
  UPDATE_USER_SUCCESS,
} from './action-types'

export function deleteUser ({ reasons, comment, password }) {
  return dispatch => {
    return manageAccount('delete', { reasons, comment, password })
  }
}

export function disableUser ({ reasons, comment, password }) {
  return dispatch => {
    return manageAccount('disable', { reasons, comment, password })
  }
}

function manageAccount (action, { reasons, comment, password }) {
  return api.manageProfileState(action, { reasons, comment, password })
}

export function loadSelfUser () {
  return dispatch => {
    return api.fetchSelf()
      .then(response => {
        dispatch(loadUserSuccess(response.data.data))
        dispatch(initAuth(true))
      }).catch(error => {
        dispatch(initAuth(false))
        dispatch(signInError())
        dispatch(loadUserError(error))
      })
  }
}

export function loadUser (targetHid) {
  return dispatch => {
    return api.loadUser({ 'target_hid': targetHid })
      .then(response => dispatch(toAction(LOAD_VIEW_USER, response.data.data)))
      .catch(error => dispatch(loadUserError(error)))
  }
}

export function updateUser (changes) {
  return dispatch => {
    return api.updateUser(changes)
      .then(response => {
        dispatch(updateUserSuccess(response.data.data))
        loadSelfUser()(dispatch)
      }).catch(error => dispatch(updateUserError(error)))
  }
}

export function updateUserInboxSize (newInboxSize) {
  return dispatch => {
    return api.updateInboxLimit({ 'max_intros': newInboxSize })
      .then(response => {
        dispatch(updateUserSuccess(response.data.data))
      }).catch(error => dispatch(updateUserError(error)))
  }
}

export function unloadUser () {
  return {
    type: UNLOAD_USER_SUCCESS,
  }
}

export function updateUserSuccess (userDetails) {
  return {
    type: UPDATE_USER_SUCCESS,
    payload: userDetails,
  }
}

function updateUserError (error) {
  return {
    type: UPDATE_USER_ERROR,
    payload: error,
  }
}

export function loadUserSuccess (userDetails) {
  return {
    type: LOAD_USER_SUCCESS,
    payload: userDetails,
  }
}

export function loadUserError (error) {
  return {
    type: LOAD_USER_ERROR,
    payload: error,
  }
}

export function removeUserSuccess () {
  return {
    type: REMOVE_USER_SUCCESS,
  }
}
