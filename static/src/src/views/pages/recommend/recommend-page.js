import PropTypes from 'prop-types'
import React, { Component } from 'react'
import Img from 'react-image'
import { FormattedMessage } from 'react-intl'
import { connect } from 'react-redux'
import { Redirect } from 'react-router-dom'
import { checkImageURL, getLoaderImageForGender } from 'src/common/utils'
import { STATE } from 'src/enums'
import { recommendationsActions } from 'src/recommendations'
import routes, { toPath } from 'src/routes'
import { userActions } from 'src/user'
import { Button, Icon, Loader, MatchActionBtns, NavHeader } from 'src/views/components'

import './recommend-page.css'

export class RecommendPage extends Component {
  constructor (props) {
    super(props)

    this.state = {
      isRecommendLoaded: false
    }
  }

  componentWillMount () {
    this.props.resetRecommendationsIndex()
    this.props.loadRecommendations()
  }

  componentWillReceiveProps (nextProps) {
    this.updateStateByProps(nextProps)
  }

  updateStateByProps () {
    this.loadRecommendations()
  }

  loadRecommendations () {
    this.setState({ isRecommendLoaded: true })
  }

  renderContent () {
    const { firstName, age, photoURL } = this.props.targetUser
    return (
      <div className='page-content-container'>
        <div className='image-container'>
          <div className="padding-holder">
            <Img
              className='user-img'
              src={ checkImageURL(photoURL) }
              decode={ false }
              loader={
                this.renderLoader()
              }
            />
            <div className="user-text-container">
              <div className='user-text'>
                <div className="user-name-age">
                  <span> { firstName },</span>
                  <span> { age } </span>
                </div>
                <Button
                  className='button-no-background button-info'
                  onClick={ () => {
                    this.showFullInfo()
                  } }>
                  <Icon name='info_outline' className='info-icon'/>
                </Button>
              </div>
            </div>

          </div>
        </div>
        <MatchActionBtns onReaction={ this.onReaction }/>
      </div>
    )
  }

  render () {
    if (this.props.user.get('state') === STATE.INCOMPLETE) {
      return <Redirect to={ routes.fill }/>
    }
    const { recommendations, isLoading, targetUser } = this.props

    if (!this.state.isRecommendLoaded) {
      return this.renderLoading()
    }

    const isReachedEndOfRecommendations = recommendations.size === 0
    if (!isLoading && !targetUser && isReachedEndOfRecommendations) {
      return this.renderNoMatchesFound()
    }

    return (
      <div className='recommend-page'>
        <NavHeader
          history={ this.props.history }
          activeRoute={ routes.recommendations }
        />
        { isLoading ? this.renderLoading() : this.renderContent() }
      </div>
    )
  }

  renderLoader () {
    const { gidIs } = this.props.targetUser
    const PersonLoader = getLoaderImageForGender(gidIs)
    return <img alt='loader' src={ PersonLoader }/>
  }

  renderLoading () {
    return (
      <Loader/>
    )
  }

  renderNoMatchesFound () {
    return (
      <div className='recommend-page'>
        <NavHeader
          history={ this.props.history }
          activeRoute={ routes.recommendations }/>
        <div className='main-page-container no-matches'>

          <div className='msg line1'><FormattedMessage id={ 'recommended.empty_box1' }/></div>
          <div className='msg line2'><FormattedMessage id={ 'recommended.empty_box2' }/></div>

          <Button
            className={ 'skip-button filled-button' }
            onClick={ this.showSkipped }>
            <FormattedMessage id={'recommended.show_skipped'}/>
          </Button>
        </div>
      </div>
    )
  }

  showSkipped = () => {
    this.props.loadSkipped()
  }

  showFullInfo = () => {
    const {
      history,
    } = this.props
    history.push(toPath(routes.recommendationsFull))
  }

  onReaction = (isMatch) => {
    const { handleReaction, history, targetUser } = this.props
    handleReaction(targetUser, isMatch, history)
  }
}

RecommendPage.propTypes = {
  auth: PropTypes.object.isRequired,
  loadUser: PropTypes.func.isRequired,
  loadRecommendations: PropTypes.func.isRequired,
  loadSkipped: PropTypes.func.isRequired,
  setUnmatch: PropTypes.func.isRequired,
  resetRecommendationsIndex: PropTypes.func.isRequired,
  incrementRecommendations: PropTypes.func.isRequired,
  isLoading: PropTypes.bool.isRequired,
}

const mapStateToProps = (state) => {
  return {
    user: state.user,
    auth: state.auth,
    recommendations: state.recommendations.list,
    recommendIndex: state.recommendations.index,
    targetUser: state.recommendations.targetUser,
    isLoading: state.recommendations.isLoadingRecommendations,
  }
}

const mapDispatchToProps = Object.assign(
  {},
  recommendationsActions,
  userActions
)

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(RecommendPage)
