import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { injectIntl } from 'react-intl'
import { connect } from 'react-redux'
import { checkImageURL } from 'src/common/utils'
import { notificationActions } from 'src/notification'
import { recommendationsActions } from 'src/recommendations'
import routes, { toPath } from 'src/routes'

import { userActions } from 'src/user'
import { BackButton, Header, Icon, Loader, MatchActionBtns } from 'src/views/components'

import './user-profile-page.css'

export class UserProfilePage extends Component {

  gotoRecommendations () {
    this.props.history.push(toPath(routes.recommendations))
  }

  componentWillMount () {
    const { isExistingMatch, match, targetUser, loadUser } = this.props

    if (isExistingMatch) {
      loadUser(match.params.id)
    } else {
      if (!targetUser) {
        this.gotoRecommendations()
      }
    }
  }

  handleFlagClick = () => {
    const {intl} = this.props
    this.props.showError(intl.formatMessage({id: 'common.feature_progress'}))
  }

  onReaction = (isMatch) => {
    const { handleReaction, history, targetUser } = this.props
    handleReaction(targetUser, isMatch, history)
  }

  render () {
    const { isExistingMatch, targetUser } = this.props

    if (!targetUser || (isExistingMatch && !targetUser.targetHid)) {
      return <Loader/>
    }
    const { age, bio, firstName, photoURL, tagline } = targetUser
    const checkedUrl = checkImageURL(photoURL)
    return (
      <div className='user-profile-page'>
        <Header absolute={ true }>
          <BackButton history={ this.props.history }/>
          <button
            onClick={ this.handleFlagClick }
            className="button"
          >
            <Icon name='flag'/>
          </button>
        </Header>
        <div className="main-part">
          <img className='user-photo' src={ checkedUrl } alt=""/>
          <div className="details-container">
            <div className="user-details-text text bold mid-large">{ firstName }, { age }</div>
            <div className="user-details-text text bold">{ tagline }</div>
            <div className="user-details-text text">{ bio }</div>
          </div>
        </div>
        { !isExistingMatch && <MatchActionBtns onReaction={ this.onReaction }/> }
      </div>
    )
  }

}

UserProfilePage.propTypes = {
  isExistingMatch: PropTypes.bool.isRequired,
  auth: PropTypes.object.isRequired,

}

const mapStateToProps = (state, props) => {
  return {
    auth: state.auth,
    user: state.user,
    targetUser: props.isExistingMatch ? state.viewUser : state.recommendations.targetUser,
  }
}

const mapDispatchToProps = Object.assign(
  {},
  notificationActions,
  recommendationsActions,
  userActions
)

export default injectIntl(connect(
  mapStateToProps,
  mapDispatchToProps
)(UserProfilePage))


