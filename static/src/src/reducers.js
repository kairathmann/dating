import { routerReducer } from 'react-router-redux'
import { combineReducers } from 'redux'
import { authReducer } from 'src/auth'
import { conversationReducer } from 'src/conversation/reducer'
import { userEditDataReducer } from 'src/editUserData/reducer'
import { signupEditDataReducer } from 'src/fillUserData/reducer'
import { messagesReducer } from 'src/messages/reducer'
import recommendationsReducer from 'src/recommendations/reducer'
import tokenReducer from 'src/token/reducer'
import userReducer, { viewUserReducer } from 'src/user/reducer'

export default combineReducers({
  auth: authReducer,
  routing: routerReducer,
  viewUser: viewUserReducer,
  user: userReducer,
  userEditData: userEditDataReducer,
  conversation: conversationReducer,
  messages: messagesReducer,
  recommendations: recommendationsReducer,
  token: tokenReducer,
  fill: signupEditDataReducer
})
