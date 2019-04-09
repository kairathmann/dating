import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { authActions } from 'src/auth'

export class LogoutPage extends Component {

  componentWillMount () {
    this.props.signOut()
  }

  render () {
    return <div/>
  }
}

LogoutPage.propTypes = {
  signOut: PropTypes.func.isRequired,
}

const mapDispatchToProps = {
  signOut: authActions.signOut,
}

export default withRouter(
  connect(
    null,
    mapDispatchToProps
  )(LogoutPage)
)
