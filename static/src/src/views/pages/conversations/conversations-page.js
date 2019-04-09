import classnames from 'classnames'
import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { FormattedMessage } from 'react-intl'
import { connect } from 'react-redux'
import { loadConversations, unloadConversations } from 'src/conversation/actions'
import routes, { toPath } from 'src/routes'
import { userActions } from 'src/user'
import { ConversationList, NavHeader } from 'src/views/components'
import './conversations-page.css'

export class ConversationsPage extends Component {

  componentWillMount () {
    this.props.unloadConversations()
    this.props.loadConversations(this.props.user.id)
  }

  renderUnreadMsgsBar (unreadMsgs) {
    const moreThan99 = unreadMsgs > 99

    return (
      <div className="unread-msgs-bar">
        <div className="title text large"><FormattedMessage id={ 'conversation.new_messages' }/></div>
        <div className="number-container">
          <div className={ classnames('number text', moreThan99 && 'small') }>
            { moreThan99 ? '99+' : unreadMsgs }
          </div>
        </div>
      </div>
    )

  }

  /*
   todo: implement this feature

   renderMsgsBeyondLimitBar(msgsBeyondLimit){
   const moreThan99 = msgsBeyondLimit > 99
   return (
   <div className="msg-box-limit-bar">
   <div className="number-container">
   <div className={classnames('number text', !moreThan99 && 'x-large')}>
   {moreThan99 ? '99+' : msgsBeyondLimit}
   </div>
   </div>
   <div className="title text thin">Messages beyond your daily inbox limit</div>
   </div>
   )
   }*/

  renderNoConversations () {
    return <span className='no-conversations-msg text double-size'>
      <FormattedMessage id={ 'conversation.empty_box' }/>
    </span>
  }

  render () {
    const { conversations, history } = this.props

    // const msgsBeyondLimit = 51 // todo: replace with real data
    const unreadMsgs = conversations.filter(c => c.pending).size
    const hasConversations = conversations.size > 0

    return (
      <div className='conversations-page'>
        <NavHeader
          history={ history }
          activeRoute={ routes.messages }/>
        <div className={ classnames('main-page-container', !hasConversations && 'no-conversations') }>
          { /*{msgsBeyondLimit > 0 && this.renderMsgsBeyondLimitBar(msgsBeyondLimit)}*/ }
          { unreadMsgs > 0 && this.renderUnreadMsgsBar(unreadMsgs) }
          { hasConversations ? (
            <ConversationList
              conversations={ conversations }
              onSelectConversation={ this.onSelectConversation }
            />
          ) : this.renderNoConversations() }
        </div>
      </div>
    )
  }

  onSelectConversation = (conversationId) => {
    this.props.history.push(toPath(routes.messages, conversationId))
  }
}

ConversationsPage.propTypes = {
  auth: PropTypes.object.isRequired,
  loadConversations: PropTypes.func.isRequired,
  unloadConversations: PropTypes.func.isRequired,
}

const mapStateToProps = (state) => {
  return {
    conversations: state.conversation.list,
    auth: state.auth,
    user: state.user,
  }
}

const mapDispatchToProps = Object.assign(
  {},
  userActions,
  { loadConversations, unloadConversations }
)

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(ConversationsPage)
