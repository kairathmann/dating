import { List } from 'immutable'
import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { STATE } from 'src/enums'
import AvatarRound from 'src/views/components/avatar-round'
import MessageItem from 'src/views/components/message-item'

import './message-list.css'

class MessageList extends Component {
  constructor (props) {
    super(props)

    this.scrollToBottom = this.scrollToBottom.bind(this)
  }

  componentWillMount () {
    this.scrollToBottom()
  }

  componentDidUpdate () {
    this.scrollToBottom()
  }

  scrollToBottom () {
    if (!this.messageListDummy) { return }
    this.messageListDummy.scrollIntoView()
  }

  handleClick = (id) => {
    const { targetUser } = this.props
    if (!(targetUser.state === STATE.DELETED || targetUser.state === STATE.DISABLED)) {
      this.props.jumpToUserView(id)
    }
  }

  shouldBeClickable = () => {
    const { targetUser } = this.props
    return !(targetUser.state === STATE.DELETED || targetUser.state === STATE.DISABLED)
  }

  render () {
    const { targetUser } = this.props
    const className = 'message-list'
    const isAnyMessages = this.props.messages && this.props.messages.size > 0
    if (!isAnyMessages) {
      return (<div className={ className }/>)
    }

    return (
      <div className={ className }>
        { targetUser.avatar &&
        <div
          className={ `message-list-avatar-container ${!this.shouldBeClickable() ? 'unclickable' : ''}` }
          onClick={ () => this.handleClick(targetUser.id) }>
          <AvatarRound
            photoURL={ targetUser.avatar.medium }
            imgClass={ 'avatar' }
            sizeInRem={ 14 }
            alt='user avatar'
          />
        </div>
        }
        <div className='message-list-messages'>
          { this.props.messages.map(m => {
            return (
              <MessageItem
                jumpToUserView={ this.props.jumpToUserView }
                key={ m.id }
                message={ m }
                userId={ this.props.userId }
              />
            )
          }) }
        </div>
        <div className="dummy" ref={ el => this.messageListDummy = el }/>
      </div>
    )
  }
}

MessageList.propTypes = {
  targetUser: PropTypes.object.isRequired,
  messages: PropTypes.instanceOf(List).isRequired,
  userId: PropTypes.string.isRequired,
  jumpToUserView: PropTypes.func.isRequired,
}

export default MessageList
