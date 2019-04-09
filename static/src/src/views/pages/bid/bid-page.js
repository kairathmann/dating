import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { findDOMNode } from 'react-dom'
import { FormattedMessage, injectIntl } from 'react-intl'
import { connect } from 'react-redux'
import { Redirect } from 'react-router'
import bgSlider from 'src/images/Likely.png'
import { createConversation } from 'src/recommendations/actions'
import routes, { toPath } from 'src/routes'
import { userActions } from 'src/user'
import { AvatarRound, BackButton, Header, StarIcon, UserMessageInput } from 'src/views/components'
// import MessageInput from 'src/views/components/user-message-input'
import './bid-page.css'

export class BidPage extends Component {
  constructor (props) {
    super(props)

    this.state = {
      amount: Math.max(1, props.token.confirmedBalance),
      message: '',
      height: '100%',
      tipLeftPx: 0,
      tipTransformLeft: 0,
    }
  }

  componentDidMount () {
    if (!this.props.targetUser) { return }
    setTimeout(() => {
      this.handleBidChange(this.state.amount) // for positioning of Tip
    }, 1)
  }

  get min () { return 0 }

  get likely () { return Math.max(1, parseFloat(this.props.targetUser.minBid)) }

  get max () { return this.likely * 20 } // todo: replace with better logic after product thinking

  calcPopularity (/*targetUser*/) {
    // some calculation for popularity
    return 1 // todo: real BE logic here
  }

  headersText (targetUser) {
    const popularity = this.calcPopularity(targetUser)
    if (popularity > 0) { // message depends on popularity
      return [
        this.props.intl.formatMessage({ id: 'bid.profile_is_popular' }, { name: targetUser.firstName }),
        this.props.intl.formatMessage({ id: 'bid.attach_stars' }),
      ]
    }
  }

  setHeightOfPageMinusMessageInputHeight = (/*messageInputHeight*/) => {
    // todo: create HOC for handling page height of pages with MessageInput stickDown
    const messageInputFullHeight = findDOMNode(this.messageInputComp).getBoundingClientRect().height
    this.setState({ height: `calc(100% - ${messageInputFullHeight}px)` })
  }

  handleSliderChange = (e) => {
    this.handleBidChange(e.target.value)
  }
  handleBidChange = (val) => {
    const sliderWidth = findDOMNode(this.sliderWrapper).getBoundingClientRect().width

    const valInPct = val / (this.max - this.min)

    this.setState({
      amount: Math.ceil(val),
      tipLeftPx: valInPct * sliderWidth,
      tipTransformLeft: (valInPct * -100), // 0% -> -100%
    })
  }

  handleBidSubmit = (val) => {
    const { createConversation, targetUser, user, history } = this.props
    const { amount } = this.state

    createConversation({
        'body': val,
        'recipient_hid': targetUser.hid,
        'sender_hid': user.id,
        'bid_price': amount.toFixed(1),
      },
      () => { history.push(toPath(routes.recommendations)) }
    )
  }

  renderBidSlider () {
    const { targetUser } = this.props
    const { amount } = this.state

    return (
      <div className='bid-slider'>
        <img className='bid-slider-bg' src={ bgSlider } alt='bgSlider'/>
        <div className='avatar-circle-wrapper'>
          <AvatarRound
            alt='Recommended user image in bid slider'
            photoURL={ targetUser.photoURL }
            sizeInRem={ 3.2 }
            floatHeight={ 1 }
          />
        </div>
        <div className='slider-wrapper' ref={ r => this.sliderWrapper = r }>
          <input
            className='slider'
            type='range'
            min={ this.min }
            max={ this.max }
            step={ 0.1 }
            value={ amount }
            onChange={ this.handleSliderChange }
          />
        </div>
      </div>
    )
  }

  renderTipLiklinessText () {
    const { amount } = this.state
    if (amount > this.likely) {
      return <span><span className='text active'> <FormattedMessage id={ 'bid.likely' }/></span> <FormattedMessage
        id={ 'bid.to_be_delivered' }/></span>
    } else {
      return (<span><span className='text active'> <FormattedMessage id={ 'bid.could' }/></span> <FormattedMessage
        id={ 'bid.be_delivered' }/></span>)
    }

  }

  renderTip () {
    const { tipTransformLeft, tipLeftPx, amount } = this.state
    const amountInPct = (amount / (this.max - this.min) * 0.78) + 0.095
    // min-max (0.1~0.9) are magic numbers, based on slide size of total image (includes the circle on right).
    // as it is only cool view. and it works almost perfect - we can live with that

    return (
      <div
        className='bid-likability-tip'
        style={ { left: tipLeftPx, transform: `translateX(${tipTransformLeft}%)` } }
      >
        <span>{ amount } </span>

        <StarIcon className='star'/>
        <span> - </span>
        { this.renderTipLiklinessText() }
        <div
          style={ { left: `${amountInPct * 100}%` } }
          className='tip-triangle-wrapper'
        >
          <div className='tip-triangle'/>
        </div>
      </div>
    )
  }

  render () {
    const { height } = this.state
    const { targetUser, token } = this.props

    if (!targetUser) { return <Redirect to={ toPath(routes.recommendations) }/> } // then it will redirect out

    const [ firstLine, secondLine ] = this.headersText(targetUser)
    return (
      <div className='bid-page' style={ { height } }>
        <Header>
          <BackButton destination={ toPath(routes.recommendations) }/>
          <div className='star-counter'>
            <div className="text">
              { token.confirmedBalance || 0 }
            </div>
            <StarIcon className='star'/>
          </div>
        </Header>
        <div className='main-page-container'>
          <AvatarRound
            alt='Recommended user image'
            photoURL={ targetUser.photoURL }
            imgClass='profile-img'
            sizeInRem={ 11.2 }
            floatHeight={ 3 }
          />
          <div className='bidding-headers text gray'>
            <div className='bidding-header first-line text bold'>{ firstLine }</div>
            <div className='bidding-header second-line text semi-thin'>{ secondLine }</div>
          </div>
          <div className='bid-slider-tip-wrapper'>
            { this.renderTip() }
            { this.renderBidSlider() }
          </div>
          <div>

          </div>
        </div>

        <UserMessageInput
          ref={ r => this.messageInputComp = r }
          onSubmit={ this.handleBidSubmit }
          onHeightChange={ this.setHeightOfPageMinusMessageInputHeight }
          stickDown
        />
      </div>
    )
  }

  handleChange = (e) => {
    let fieldName = e.target.name
    this.setState({
      [ fieldName ]: e.target.value,
    })
  }

}

BidPage.propTypes = {
  auth: PropTypes.object.isRequired,
  targetUser: PropTypes.object, // if not present - redirect
  createConversation: PropTypes.func.isRequired,
  token: PropTypes.shape({
    confirmedBalance: PropTypes.number,
    unconfirmedBalance: PropTypes.number,
  }).isRequired,
}

const mapStateToProps = (state) => {
  return {
    token: state.token,
    user: state.user,
    auth: state.auth,
    targetUser: state.recommendations.targetUser,
  }
}

const mapDispatchToProps = Object.assign(
  {},
  userActions,
  { createConversation }
)

export default injectIntl(
  connect(
    mapStateToProps,
    mapDispatchToProps
  )(BidPage))
