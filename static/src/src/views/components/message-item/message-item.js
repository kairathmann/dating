import classNames from 'classnames'
import 'moment-timezone'
import PropTypes from 'prop-types'
import React, { Component } from 'react'
import Moment from 'react-moment'
import { connect } from 'react-redux'
import { STATE } from 'src/enums'

import AvatarRound from 'src/views/components/avatar-round'

import './message-item.css'

export class MessageItem extends Component {

  isFromUser = () => {
    return (this.props.message.senderHid === this.props.user.id)
  }

  render () {
    const messageAlignClass = classNames({
      'message-item': true,
      'align-right': this.isFromUser(),
    })
    return (
      <div className={ messageAlignClass }>
        { this.renderFrom() }
        { this.renderBody() }
      </div>
    )
  }

  handleJumpTo = () => {
    const { message } = this.props
    if (!this.isFromUser() && !(message.state === STATE.DELETED || message.state === STATE.DISABLED)) {
      this.props.jumpToUserView(this.props.message.senderHid)
    }
  }

  shouldBeClickable = () => {
    const { message } = this.props
    return !(message.state === STATE.DELETED || message.state === STATE.DISABLED)
  }

  renderFrom () {
    const { user, message } = this.props
    const TODO_AVATAR = this.isFromUser() ? user.photoURL : message.avatarSmall
    return (
      <div
        className={ `message-item-from ${ !this.shouldBeClickable() ? 'unclickable' : ''}` }
        onClick={ this.handleJumpTo }>
        <AvatarRound
          photoURL={ TODO_AVATAR }
          imgClass={ 'avatar' }
          sizeInRem={ 3.67 }
          alt='user avatar'
        />
      </div>
    )
  }

  renderCreated () {
    const { message } = this.props
    return (
      <div className='message-item-created'>
        <span><Moment fromNow>{ message.sent_time }</Moment></span>
      </div>
    )
  }

  renderBody () {
    const messageBodyClass = classNames(
      'text message-body',
      {
        'is-from-user': this.isFromUser(),
      })
    const { message } = this.props
    return (
      <div className={ messageBodyClass }>
        { message.body }
      </div>
    )
  }
}

MessageItem.propTypes = {
  message: PropTypes.shape({
    body: PropTypes.string,
    id: PropTypes.number,
    is_recipient: PropTypes.bool,
    recipient_hid: PropTypes.string,
    sender_avatar: PropTypes.string,
    sender_hid: PropTypes.string,
    sender_name: PropTypes.string,
    sender_gender: PropTypes.number,
    sent_time: PropTypes.string,
  }).isRequired,
  user: PropTypes.object.isRequired,
  jumpToUserView: PropTypes.func.isRequired,

}

const mapStateToProps = (state) => {
  return {
    user: state.user,
  }
}

export default connect(
  mapStateToProps,
  {}
)(MessageItem)
