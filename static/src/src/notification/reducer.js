import { Record } from 'immutable'
import { SHOW_ERROR, SHOW_SUCCESS } from './action-types'

export const NotificationState = new Record({
  message: '',
  type: '',
})

export function notificationReducer (state = new NotificationState(), action) {
  switch (action.type) {
    case SHOW_ERROR:
      return state.merge({
        display: true,
        type: 'error',
        message: action.payload,
      })

    case SHOW_SUCCESS:
      return state.merge({
        display: true,
        type: 'success',
        message: action.payload,
      })

    default:
      return new NotificationState()
  }
}
