import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { findDOMNode } from 'react-dom'
import { FormattedMessage, injectIntl } from 'react-intl'
import { connect } from 'react-redux'
import { Redirect } from 'react-router-dom'
import { BID_STATUS, STATE } from 'src/enums'
import { messagesActions } from 'src/messages'
import { notificationActions } from 'src/notification'
import { recommendationsActions } from 'src/recommendations'
import routes, { toPath } from 'src/routes'
import { userActions } from 'src/user'
import { BackButton, Button, Header, Icon, MessageList, UserMessageInput } from 'src/views/components'
import './message-page.css'

export class MessagePage extends Component {

  constructor (props) {
    super(props)
    this.state = {
      height: '100%',
    }
  }

  get targetUser () {
    const {
      targetUser,
      isExistingMatch,
      selectedConversation
    } = this.props

    if (isExistingMatch) {
      return {
        avatar: selectedConversation && {
          small: selectedConversation.get('avatarSmall'),
          medium: selectedConversation.get('avatarMedium')
        },
        name: selectedConversation && selectedConversation.get('partnerName'),
        id: selectedConversation && selectedConversation.get('partnerId'),
        gender: selectedConversation && selectedConversation.get('partnerGender'),
        state: selectedConversation && selectedConversation.get('partnerState')
      }
    } else {
      return targetUser
    }
  }

  componentWillMount () {
    // We might not have conversationId if this is the first time the user bids
    const conversationId = this.props.match.params.id

    this.shouldLoadConversation(conversationId)
    this.polling = setInterval(() => {
      this.shouldLoadConversation(conversationId)
    }, MessagePage.POLLING_INTERVAL)
  }

  componentWillUnmount () {
    clearInterval(this.polling)
  }

  componentDidMount () {
    // Check if this is a newly conversation
    const targetUserId = this.props.match.params.targetUserId
    if (targetUserId) {
      this.props.unloadMessages()
    }

    this.setHeightOfPageMinusMessageInputHeight()
    this.scrollToListBottom()

  }

  componentWillReceiveProps (nextProps) {
    this.shouldRedirectToMessage(nextProps)
  }

  shouldLoadConversation = (conversationId) => {
    if (conversationId) {
      this.props.loadMessages(this.props.user.id, parseInt(conversationId, 10))
    }
  }

  scrollToListBottom = () => {
    !!this.ml && this.ml.scrollToBottom()
  }

  setHeightOfPageMinusMessageInputHeight = () => {
    // todo: create HOC for handling page height of pages with MessageInput stickDown
    const $el = findDOMNode(this.messageInputComp)
    if (!$el) { return }
    const messageInputFullHeight = $el.getBoundingClientRect().height

    this.setState({ height: messageInputFullHeight })
  }

  shouldRedirectToMessage = (nextProps) => {
    if (nextProps.lastReactionConversationId !== this.props.lastReactionConversationId) {
      this.props.history.push(toPath(routes.messages, nextProps.lastReactionConversationId))
      this.shouldLoadConversation(nextProps.lastReactionConversationId)
    }
  }

  handleSubmitMessage = (message) => {
    // This will be given only for the first time a user message happens
    const targetUserId = this.props.match.params.targetUserId
    if (targetUserId) {
      this.props.createConversation({
          'body': message,
          'recipient_hid': targetUserId,
          'sender_hid': this.props.user.id,
          'bid_price': '0.0',
        },
        () => { this.props.history.push(toPath(routes.recommendations)) })
    } else {
      return this.props.sendMessage({
        body: message,
        targetUser: this.props.selectedConversation.get('partnerId'),
      })
    }
  }

  jumpToUserView = (id) => {
    this.props.history.push(toPath(routes.user, id))
  }

  renderWaitingForBidApprove () {
    return (
      <div className='waiting-for-approval-msg'>
        <p>
          <FormattedMessage id={ 'message.msg_sent' }/>
        </p>
      </div>
    )
  }

  renderUserMsgInput () {
    return (
      <UserMessageInput
        stickDown
        sendState={ this.props.sendState }
        onSubmit={ this.handleSubmitMessage }
        conversationId={ this.props.match.params.id }
        ref={ r => this.messageInputComp = r }
        onHeightChange={ this.setHeightOfPageMinusMessageInputHeight }
      />
    )
  }

  render () {
    const targetUser = this.targetUser

    if (!targetUser) {
      return (
        <Redirect to={ {
          pathname: toPath(routes.recommendations),
          state: { from: this.props.location },
        } }/>
      )
    }

    const { height } = this.state
    const { isExistingMatch, selectedConversation } = this.props

    const backDestination = toPath(isExistingMatch ? routes.messages : routes.recommendations)
    const isWaitingForBitApprove = isExistingMatch && selectedConversation && selectedConversation.get('bidStatus') === BID_STATUS.BID_WON

    return (
      <div className='message-page' style={ { height: `calc(100% - ${height}px)` } }>
        <Header>
          <BackButton destination={ backDestination }/>
          <h1 onClick={ () => {this.jumpToUserView(targetUser.id)} }>
            <span>{ targetUser.name }</span>
          </h1>
          <span className='float-right'>
            <Button
              className='button-no-border button-no-background'
              onClick={ this.flagUser }>
              <Icon name='flag'/>
            </Button>
          </span>
        </Header>
        <div className="message-page-body">
          <MessageList
            jumpToUserView={ this.jumpToUserView }
            messages={ this.props.messages }
            targetUser={ targetUser }
            userId={ this.props.user.id }
          />
        </div>
        { targetUser && !(targetUser.state === STATE.DELETED || targetUser.state === STATE.DISABLED) &&
        <div>
          { isWaitingForBitApprove ? this.renderWaitingForBidApprove() : this.renderUserMsgInput() }
        </div>
        }
      </div>
    )
  }

  flagUser = () => {
    const {intl} = this.props
    this.props.showError(intl.formatMessage({id: 'common.feature_progress'}))
  }
}

MessagePage.POLLING_INTERVAL = 10000

MessagePage.propTypes = {
  auth: PropTypes.object.isRequired,
  user: PropTypes.object.isRequired,
  loadMessages: PropTypes.func.isRequired,
  unloadMessages: PropTypes.func.isRequired,
  sendMessage: PropTypes.func.isRequired,
  createConversation: PropTypes.func.isRequired,
  showError: PropTypes.func.isRequired,
  isExistingMatch: PropTypes.bool.isRequired,
  selectedConversation: PropTypes.object,
}

MessagePage.defaultProps = {}

const mapStateToProps = (state) => {
  return {
    auth: state.auth,
    user: state.user,
    messages: state.messages.list,
    sendState: state.messages.sendState,
    selectedConversation: state.messages.selectedConversation,
    lastReactionConversationId: state.recommendations.lastReactionConversationId,
    recommendations: state.recommendations.list,
    recommendIndex: state.recommendations.index,
    targetUser: state.recommendations.targetUser,
    conversations: state.conversation.list,
  }
}

const mapDispatchToProps = Object.assign(
  {},
  userActions,
  messagesActions,
  notificationActions,
  recommendationsActions
)

export default injectIntl(connect(
  mapStateToProps,
  mapDispatchToProps
)(MessagePage))
