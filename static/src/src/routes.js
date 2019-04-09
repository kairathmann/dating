const tokensRoute = 'tokens'
export const token = 'token'

export default {
  // id: route name
  welcome: 'welcome',
  login: 'login',
  signup: 'signup',
  forgotPassword: 'forgot',
  resetPassword: 'auth/forgot-pass', // sent here from mail
  confirmEmail: 'auth/confirm-email', // sent here from mail
  logout: 'logout',
  viewProfile: 'me',
  editProfile: 'editmyprofile',
  messages: 'messages',
  newMessage: 'messages/new',
  recommendations: 'findlove',
  recommendationsFull: 'findlove/view',
  user: 'user',
  bid: 'isthistheone',
  tokenBalance: `${tokensRoute}`,
  deposit: `${tokensRoute}/deposit`,
  withdraw: `${tokensRoute}/withdraw`,
  transactionHistory: `${tokensRoute}/history`,
  fill: `fillprofile`,
  disable: 'disable'
}

export function toParam (param) {
  return ':' + param
}

export function toPath (...strings) {
  return '/' + strings.join('/')
}

export function getPath (location) {
  return location.pathname.slice(1).split('/')
}

export function pathStartWith (location, ...strings) {
  return location.pathname.startsWith(toPath(...strings))
}

export function getLastPathRoute (location) {
  const path = getPath(location)
  return path[ path.length - 1 ]
}
