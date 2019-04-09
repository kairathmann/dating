import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { FormattedMessage } from 'react-intl'
import { withRouter } from 'react-router-dom'
import Icon from 'src/views/components/icon'

import './back-button.css'

class BackButton extends Component {
  render () {
    return (
      <button
        className="button back-button"
        onClick={ this.goBack }>
        { this.props.text ?
          <span><FormattedMessage id={ this.props.text }/></span>
          :
          <Icon name='arrow_back'/>
        }
      </button>
    )
  }

  goBack = () => {
    const { history, destination, onBack } = this.props
    if (destination) {
      history.replace(destination)
    } else {
      history.goBack()
    }
    if (onBack) {
      onBack()
    }
  }
}

BackButton.propTypes = {
  history: PropTypes.object,
  destination: PropTypes.string,
  text: PropTypes.string,
  onBack: PropTypes.func
}

export default withRouter(BackButton)
