import { toast } from 'react-toastify'
import { DISMISS_NOTIFICATION, SHOW_ERROR, SHOW_SUCCESS } from './action-types'

export function dismissNotification () {
  return {
    type: DISMISS_NOTIFICATION,
  }
}

export function showError (message) {
  toast.error(message)
  return {
    type: SHOW_ERROR,
    payload: message,
  }
}

export function showSuccess (message) {
  toast(message)
  return {
    type: SHOW_SUCCESS,
    payload: message,
  }
}
