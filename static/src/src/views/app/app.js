import PropTypes from 'prop-types'
import React from 'react'
import { connect } from 'react-redux'
import { Redirect, Switch, withRouter } from 'react-router-dom'
import 'react-select/dist/react-select.css'

import { ToastContainer } from 'react-toastify'
import 'react-toastify/dist/ReactToastify.min.css'

import { authActions } from 'src/auth'
import routes, { token, toParam, toPath } from 'src/routes'
import { loadSelfUser } from 'src/user/actions'

import { RequireAuthRoute, RequireUnauthRoute } from 'src/views/components/require-auth-route'
import BidPage from 'src/views/pages/bid/bid-page'
import ConversationsPage from 'src/views/pages/conversations/conversations-page'
import DisablePage from 'src/views/pages/disable/disable-page'
import EditProfilePage from 'src/views/pages/edit-profile/edit-profile-page'
import FillProfilePage from 'src/views/pages/fill-profile/fill-profile-page'
import ForgotPage from 'src/views/pages/forgot/forgot-page'
import LoginPage from 'src/views/pages/login/login-page'
import LogoutPage from 'src/views/pages/logout/logout-page'
import MessagePage from 'src/views/pages/message/message-page'
import ProfilePage from 'src/views/pages/profile/profile-page'
import RecommendPage from 'src/views/pages/recommend/recommend-page'
import ResetPassPage from 'src/views/pages/reset-pass/reset-pass'
import SignupPage from 'src/views/pages/signup/signup-page'
import DepositPage from 'src/views/pages/token-pages/deposit/deposit-page'
import TokenBalance from 'src/views/pages/token-pages/token-balance/token-balance'
import UserProfilePage from 'src/views/pages/userProfile/user-profile-page'

import WelcomePage from 'src/views/pages/welcome/welcome-page'
import WithdrawPage from 'src/views/pages/withdraw/withdraw-page'

const App = props => {
  const { auth, user } = props
  if (user.isNotFetchedYet) {
    props.loadSelfUser()
  }
  return (
    <main className='luna-app-main'>
      <ToastContainer
        position='top-right'
        autoClose={ 5000 }
        hideProgressBar={ false }
        newestOnTop={ true }
        pauseOnHover
      />

      <Switch>
        <RequireUnauthRoute auth={ auth } exact path='/' component={ WelcomePage }/>
        <RequireAuthRoute auth={ auth } path={ toPath(routes.confirmEmail, toParam(token)) } component={ ProfilePage }/>
        <RequireAuthRoute auth={ auth } path={ toPath(routes.fill) } component={ FillProfilePage }/>
        <RequireUnauthRoute auth={ auth } path={ toPath(routes.welcome) } component={ WelcomePage }/>
        <RequireUnauthRoute auth={ auth } path={ toPath(routes.login) } component={ LoginPage }/>
        <RequireUnauthRoute auth={ auth } path={ toPath(routes.signup) } component={ SignupPage }/>
        <RequireUnauthRoute auth={ auth } path={ toPath(routes.forgotPassword) } component={ ForgotPage }/>
        <RequireUnauthRoute auth={ auth } path={ toPath(routes.resetPassword, toParam(token)) }
                            component={ ResetPassPage }/>
        <RequireUnauthRoute auth={ auth } path={ toPath(routes.logout) } component={ LogoutPage }/>
        <RequireAuthRoute auth={ auth } path={ toPath(routes.viewProfile) } component={ ProfilePage }/>
        <RequireAuthRoute auth={ auth } path={ toPath(routes.editProfile) } component={ EditProfilePage }/>
        <RequireAuthRoute
          auth={ auth } exact
          path={ toPath(routes.messages) }
          component={ ConversationsPage }
        />
        <RequireAuthRoute
          auth={ auth }
          exact path={ toPath(routes.recommendations) }
          component={ RecommendPage }
        />
        <RequireAuthRoute
          auth={ auth }
          exact path={ toPath(routes.recommendationsFull) }
          component={ UserProfilePage }
          componentProps={ { isExistingMatch: false } }
        />
        <RequireAuthRoute
          auth={ auth }
          exact path={ toPath(routes.user, ':id') }
          component={ UserProfilePage }
          componentProps={ { isExistingMatch: true } }
        />
        <RequireAuthRoute
          auth={ auth }
          exact path={ toPath(routes.messages, ':id') }
          component={ MessagePage }
          componentProps={ { isExistingMatch: true } }
        />
        <RequireAuthRoute
          auth={ auth }
          path={ toPath(routes.newMessage, ':targetUserId') }
          component={ MessagePage }
          componentProps={ { isExistingMatch: false } }
        />
        <RequireAuthRoute
          auth={ auth }
          path={ toPath(routes.disable) }
          component={ DisablePage }
          componentProps={ { isExistingMatch: false } }
        />
        <RequireAuthRoute auth={ auth } path={ toPath(routes.bid) } component={ BidPage }/>
        { /*<RequireAuthRoute auth={auth} path={toPath(routes.transactionHistory)} component={DepositPage}/>*/ }
        <RequireAuthRoute auth={ auth } exact path={ toPath(routes.tokenBalance) } component={ TokenBalance }/>
        <RequireAuthRoute auth={ auth } path={ toPath(routes.deposit) } component={ DepositPage }/>
        <RequireAuthRoute auth={ auth } path={ toPath(routes.withdraw) } component={ WithdrawPage }/>

        <Redirect
          to={ toPath(routes.welcome) }/> { /* when no matching route, redirect to home page. this will redirect to profile if logged in*/ }
      </Switch>
    </main>
  )
}
App.propTypes = {
  auth: PropTypes.object.isRequired,
  signOut: PropTypes.func.isRequired,
}

const mapStateToProps = (state) => {
  return {
    user: state.user,
    auth: state.auth,
  }
}

const mapDispatchToProps = {
  loadSelfUser,
  signOut: authActions.signOut,
}

export default withRouter(
  connect(
    mapStateToProps,
    mapDispatchToProps
  )(App)
)
