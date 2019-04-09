import { List } from 'immutable'
import PropTypes from 'prop-types'
import React, { Component } from 'react'
import ConversationItem from 'src/views/components/conversation-item/conversation-item'

import './conversation-list.css'

class ConversationList extends Component {
  render () {
    const isAnyConversations = this.props.conversations && this.props.conversations.size > 0
    if (!isAnyConversations) {
      return (<div/>)
    }

    let conversationItems = this.props.conversations.map((conversation, index) => {
      return (
        <ConversationItem
          key={ index }
          conversation={ conversation }
          onSelectConversation={ this.props.onSelectConversation }
        />
      )
    })

    return (
      <div className='conversation-list'>
        { conversationItems }
      </div>
    )
  }
}

ConversationList.propTypes = {
  conversations: PropTypes.instanceOf(List).isRequired,
  onSelectConversation: PropTypes.func.isRequired,
}

export default ConversationList
