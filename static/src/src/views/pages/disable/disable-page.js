import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { FormattedMessage, injectIntl } from 'react-intl'
import { connect } from 'react-redux'
import { signOut } from 'src/auth/actions'
import { showError } from 'src/notification/actions'
import routes from 'src/routes'
import { deleteUser, disableUser } from 'src/user/actions'
import { Button, Header, HeaderTitle, Icon, Questionnaire } from '../../components'

import './disable-page.css'

export class DisablePage extends Component {

  constructor (props) {
    super(props)
    this.state = {
      disable: false,
      delete: false,
      error: ''
    }
  }

  handleDisable = async (payload) => {
    const { disable } = this.state
    const { intl } = this.props
    if (disable) {
      try {
        await this.props.disableUser(payload)
        await this.props.signOut()
        await this.props.showError(intl.formatMessage({id: 'disable.account_disabled'}))
      } catch (err) {
        this.setState({
          error: err.response.data.code === 'wrong_password'
            ? intl.formatMessage({id: 'common.wrong_password'})
            : intl.formatMessage({id: 'common.server_error'})
        })
      }
    } else {
      this.setState({
        disable: true
      })
    }
  }

  handleDeleting = async (payload) => {
    const { delete: deleting } = this.state
    const { intl } = this.props
    if (deleting) {
      try {
        await this.props.deleteUser(payload)
        await this.props.signOut()
        await this.props.showError(intl.formatMessage({id: 'disable.account_deleted'}))
      } catch (err) {
        this.setState({
          error: err.response.data.code === 'wrong_password'
            ? intl.formatMessage({id: 'common.wrong_password'})
            : intl.formatMessage({id: 'common.server_error'})
        })
      }
    } else {
      this.setState({
        delete: true
      })
    }
  }

  handleBack = () => {
    const { disable, delete: deleting } = this.state
    if (disable || deleting) {
      this.setState({ disable: false, delete: false, error: '' })
    } else {
      this.props.history.replace(routes.editProfile)
    }
  }

  renderDisable = () => {
    const { disable, delete: deleting } = this.state
    const { intl } = this.props

    if (deleting) return <div/>
    return (
      <div>
        <h3><FormattedMessage id={ 'disable.disable_header' }/></h3>
        <p><FormattedMessage id={ 'disable.disable_description' }/></p>
        { disable &&
        <div className='questionnaire-container'>
          <Questionnaire
            error={ this.state.error }
            confirmText={ intl.formatMessage({ id: 'disable.disable_confirm' }) }
            onConfirm={ this.handleDisable }/>
        </div>
        }
        { !disable &&
        <Button className="manage-button filled-button" onClick={ this.handleDisable }><FormattedMessage
          id={ 'disable.disable_submit' }/></Button>
        }
        <p/>
      </div>
    )
  }

  renderDeleting = () => {
    const { disable, delete: deleting } = this.state
    const { intl } = this.props
    if (disable) return <div/>
    return (
      <div>
        <h3><FormattedMessage id={ 'disable.delete_header' }/></h3>
        <p><FormattedMessage id={ 'disable.delete_description' }/></p>
        { deleting &&
        <div className='questionnaire-container'>
          <Questionnaire
            error={ this.state.error }
            confirmText={ intl.formatMessage({ id: 'disable.delete_confirm' }) }
            onConfirm={ this.handleDeleting }/>
        </div>
        }
        { !deleting &&
        <Button className="manage-button filled-button" onClick={ this.handleDeleting }><FormattedMessage
          id={ 'disable.delete_submit' }/></Button>
        }
      </div>
    )
  }

  renderBackButton () {
    return (
      <button
        className="button back-button"
        onClick={ this.handleBack }>
        <Icon name='arrow_back'/>
      </button>
    )
  }

  render () {
    const { intl } = this.props
    return (
      <div className='disable-page'>
        <Header equalSidesForStrictCenter>
          { this.renderBackButton() }
          <HeaderTitle title={ intl.formatMessage({id: 'disable.manage'})}/>
          <div/>
        </Header>
        <div className='manage-account-container'>
          <div className='manage-buttons'>
            { this.renderDisable() }
            { this.renderDeleting() }
            { (this.state.disable || this.state.delete) &&
            <Button className="manage-button link-button"
                    onClick={ () => this.setState({ disable: false, delete: false, error: '' }) }><FormattedMessage
              id={ 'common.cancel' }/></Button>
            }
          </div>
        </div>
      </div>
    )
  }
}

DisablePage.propTypes = {
  deleteUser: PropTypes.func.isRequired,
  disableUser: PropTypes.func.isRequired,
  signOut: PropTypes.func.isRequired
}

const mapDispatchToProps = Object.assign(
  {},
  { deleteUser, disableUser, signOut, showError }
)

export default injectIntl(connect(
  null,
  mapDispatchToProps
)(DisablePage))
