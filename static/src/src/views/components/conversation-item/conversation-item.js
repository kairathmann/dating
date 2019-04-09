import 'moment-timezone'
import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { FormattedMessage } from 'react-intl'
import Moment from 'react-moment'
import { connect } from 'react-redux'
import AvatarRound from 'src/views/components/avatar-round'

import './conversation-item.css'

export class ConversationItem extends Component {

  zoneOffset = new Date().getTimezoneOffset()

  selectConversation = () => {
    return this.props.onSelectConversation(this.props.conversation.id)
  }

  renderAvatar () {
    const { conversation: { avatarSmall, pending } } = this.props
    const isUnreadMsg = pending

    return (
      <div className='avatar-container'>
        <AvatarRound
          alt='avatar'
          photoURL={ avatarSmall }
          imgClass={ 'avatar' }
          sizeInRem={ 7.5 }
        />
        { isUnreadMsg && <div className="unread-message-indicator"/> }
      </div>
    )
  }

  renderUpdateTime () {
    return (
      <div className='message-date text small thin'>
        <span><Moment fromNow subtract={ { minutes: this.zoneOffset } }>{ this.props.conversation.lastUpdate }</Moment></span>
      </div>
    )
  }

  renderUserName () {
    return (
      <div className="user-name text large">{ this.props.conversation.partnerName }</div>
    )
  }

  renderBodyMessage () {
    const { conversation } = this.props
    const isYou = (conversation.last_message_sender_hid === this.props.user.id) ? 'You: ' : ''

    const lastMsgText = (() => {
      const maxMsgLength = 60 //todo: plz review this and play with numbers
      const msg = conversation.subject
      if (msg && msg.length > (maxMsgLength + 2)) {
        return `${msg.slice(0, maxMsgLength)}...`
      }
      return msg
    })()

    return (
      <div className='message-body text small semi-black'>
        { isYou && <span className="from-you"><FormattedMessage id='common.you'/></span> }
        <span className="msg-body">
          { lastMsgText }
        </span>
      </div>
    )
  }

  renderBody () {
    return (
      <div className='body-container text semi-black semi-thin'>
        <div className="body-main">
          { this.renderUserName() }
          { this.renderBodyMessage() }
        </div>
        { this.renderUpdateTime() }
      </div>
    )
  }

  render () {
    return (
      <div className='conversation-item' onClick={ this.selectConversation }>
        { this.renderAvatar() }
        { this.renderBody() }
      </div>
    )
  }

}

ConversationItem.propTypes = {
  conversation: PropTypes.shape({
    id: PropTypes.number,
    partner_hid: PropTypes.string,
    partner_name: PropTypes.string,
    partner_avatar: PropTypes.string, // url
    last_update: PropTypes.string, // time
    last_message_sender_hid: PropTypes.string,
    pending: PropTypes.bool,
    subject: PropTypes.string,
  }).isRequired,
  auth: PropTypes.object.isRequired,
  onSelectConversation: PropTypes.func.isRequired,
}

const mapStateToProps = (state) => {
  return {
    user: state.user,
    auth: state.auth,
  }
}

export default connect(
  mapStateToProps,
  {}
)(ConversationItem)
