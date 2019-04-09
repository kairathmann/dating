import PropTypes from 'prop-types'
import React, { Component } from 'react'
import Img from 'react-image'
import { FormattedMessage } from 'react-intl'
import { connect } from 'react-redux'
import { Redirect } from 'react-router-dom'
import { authActions } from 'src/auth'
import { notificationActions } from 'src/notification'
import routes, { pathStartWith, token, toPath } from 'src/routes'
import { userActions } from 'src/user'
import { isUserMissingCriticalDetails } from 'src/user/user'
import { Button, Icon, NavHeader, StarIcon } from 'src/views/components'

import './profile-page.css'

export class ProfilePage extends Component {

  componentWillMount () {
    const { location, match } = this.props
    if (pathStartWith(location, routes.confirmEmail)) {
      // if this was a confirm redirection from email - post confirmation to server
      this.props.confirmEmail(match.params[ token ])
      this.props.history.replace(toPath(routes.viewProfile)) // no success/error handling. If confirmation did not
                                                             // succeed no way to know that. todo: design flow for this
    }
  }

  render () {
    if (isUserMissingCriticalDetails(this.props.user)) {
      // todo: this can be HOC, let's think about it together
      return (
        <Redirect to={ {
          pathname: toPath(routes.editProfile),
        } }/>
      )
    }
    return (
      <div className='profile-page'>
        <NavHeader
          history={ this.props.history }
          activeRoute={ routes.viewProfile }/>
        <div className='main-page-container'>
          <div className="scroll-container">
            <div className='profile-image-container'>
              <Img
                className='profile-image'
                src={ this.props.user.photoURL }
                alt={ 'User profile image' }/>
            </div>
            <div className="profile-details">
              <div className='profile-header text bold mid-large'>
                { this.props.user.name }, { this.props.user.age }
                <span className='stars'>{ this.props.user.balance.confirmedBalance }<StarIcon/></span>
              </div>
              <div className='tagline text x-bold x-large'>
                { this.props.user.tagline }
              </div>
              <div className='bio'>
                { this.props.user.bio }
              </div>

            </div>
          </div>
          <div className='actions'>
            <Button
              className="logout-btn"
              onClick={ () => {
                this.props.signOut()
              } }>
              <Icon name={ 'power_settings_new' }/>
            </Button>
            <Button
              className="edit-profile-btn"
              onClick={ () => {
                this.props.history.push(routes.editProfile)
              } }>
              <span className='text bold x-large semi-black'>
                <FormattedMessage id={'common.edit_upper'}/>
                <br/>
                <FormattedMessage id={'common.profile_upper'}/>
              </span>
            </Button>
            <Button
              className="buy-stars-btn"
              onClick={ () => {
                this.props.history.push(routes.tokenBalance)
              } }>
              <span className="buy-stars-text text bold double-size semi-black">
                TOKEN
              </span>
              <StarIcon className="buy-stars-icon"/>
            </Button>
          </div>
        </div>
      </div>
    )
  }
}

ProfilePage.propTypes = {
  auth: PropTypes.object.isRequired,
}

const mapStateToProps = (state) => {
  return {
    user: state.user,
    auth: state.auth,
  }
}

const mapDispatchToProps = Object.assign(
  {},
  userActions,
  notificationActions,
  authActions
)

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(ProfilePage)
