import classNames from 'classnames'
import React, { Component } from 'react'
import { FormattedMessage } from 'react-intl'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import routes from 'src/routes'
import { Button, LunaLogo } from '../../components'
import { LOGOS, TYPES } from 'src/views/components/luna-logo/luna-logo'

import './welcome-page.css'

class WelcomePage extends Component {

  constructor (props) {
    super(props)
    this.state = {
      intervalId: null,
      animate: false,
    }
  }

  login = () => {
    this.props.history.push(routes.login)
  }

  signup = () => {
    this.props.history.push(routes.signup)
  }

  animateBackground = () => {
    clearInterval(this.state.intervalId)
    this.setState({ animate: true })
  }

  componentDidMount () {
    const intervalId = setInterval(this.animateBackground, WelcomePage.ANIMATION_TIME)
    this.setState({ intervalId: intervalId })
  }

  componentWillUnmount () {
    if (this.state.intervalId) {
      clearInterval(this.state.intervalId)
    }
  }

  render () {
    const { animate } = this.state

    const animateClassName = classNames({
      'background-luna': true,
      'blurred': animate,
    })

    const buttonClassName = classNames({
      'welcome-buttons': true,
      'hidden': !animate,
    })

    return (
      <div className={ classNames('welcome') }>
        <div className={ animateClassName } alt='woman bg'/>
        <div className="container">
          <div className='header-container'>
            <LunaLogo name={ LOGOS.wb_trimmed } type={ TYPES.logo }/>
            <h2 className='tag-line'><FormattedMessage id='welcome.subtitle'/></h2>
          </div>
          <div className={ buttonClassName }>
            <Button className="welcome-button filled-button" onClick={ this.signup }><FormattedMessage id='welcome.sign_up'/></Button>
            <Button className="welcome-button link-button" onClick={ this.login }><FormattedMessage id='welcome.login'/></Button>
          </div>
        </div>
      </div>
    )
  }
}

WelcomePage.ANIMATION_TIME = 1000

export default withRouter(connect(null, {})(WelcomePage))
