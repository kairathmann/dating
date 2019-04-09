import PropTypes from 'prop-types'
import { Line } from 'rc-progress'
import React, { Component } from 'react'
import { FormattedMessage } from 'react-intl'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { authActions } from 'src/auth'
import { saveChanges, startFillData, updateUser } from 'src/fillUserData/actions'
import routes from 'src/routes'
import { Icon } from 'src/views/components'

import './fill-profile-page.css'
import { AboutStep, GenderStep, SettingsStep, TaglineStep, UploadStep } from './steps'

const STEPS = [
  { order: 1, component: AboutStep },
  { order: 2, component: GenderStep },
  { order: 3, component: UploadStep },
  { order: 4, component: SettingsStep },
  { order: 5, component: TaglineStep }
]

export class FillProfilePage extends Component {

  constructor (props) {
    super(props)
    this.state = {
      currentStep: STEPS[ 0 ].order,
      allDone: false,
      isError: false
    }
  }

  componentDidMount () {
    this.props.startFillData()
    const step = this.calculateStep(this.props.createdUser)

    this.setState({
      currentStep: step
    })
  }

  calculateStep (user) {
    // Check only name because updating name and birthday is atomic in this flow
    if (!(user.get('name'))) return STEPS[ 0 ].order
    if (!(user.get('gender') && user.get('sexuality'))) return STEPS[ 1 ].order

    return STEPS[ 2 ].order
  }

  renderSteps () {
    const { currentStep, isError } = this.state
    return (
      <div className='fill-profile'>
        <div className='in-row-container'>
          <button
            className="button back-button item"
            onClick={ this.handleBack }>
            <Icon name='arrow_back'/>
          </button>
          <div className='item middle stepper'>
            <Line percent={currentStep * 100/6} trailWidth='4'strokeWidth='4' strokeColor={'#603a93'}/>
          </div>
          <div className='item'/>
        </div>
        { this.renderCurrentStep() }
        { isError && (
          <p className={'red'}>Something went wrong</p>
        )}
      </div>
    )
  }

  renderAllDone () {
    return (<div className='fill-profile no-padding'>
      <div className='all-done'>
        <div className='msg line1 title'><FormattedMessage id={ 'fill.all_done' }/></div>
        <div className='msg line2'><FormattedMessage id={ 'fill.looking_for' }/></div>
      </div>
    </div>)
  }

  render () {
    return !this.state.allDone ? this.renderSteps() : this.renderAllDone()
  }

  renderCurrentStep () {
    const { currentStep } = this.state
    const props = {
      onUpdate: this.handleUpdate,
      user: this.props.user
    }
    const { component: Component } = STEPS.find(s => s.order === currentStep)
    return <Component { ...props }/>
  }

  handleUpdate = async (changes) => {
    try {
      await this.props.updateUser(changes)
      await this.props.saveChanges(changes)
      if (this.state.currentStep === STEPS[ 4 ].order) {
        await this.props.saveChanges(this.props.user)
        this.setState({
          allDone: true,
          isError: false
        })
        setTimeout(() => {
          this.props.history.push({ pathname: routes.recommendations })
        }, 2000)
      } else {
        this.setState({
          currentStep: this.state.currentStep + 1,
          isError: false
        })
      }
    } catch (err) {
      this.setState({
        isError: true
      })
    }
  }

  handleBack = () => {
    let { currentStep } = this.state
    if (currentStep === STEPS[ 0 ].order) {
      this.props.signOut()
    } else {
      this.setState({
        currentStep: currentStep - 1
      })
    }
  }
}

FillProfilePage.propTypes = {
  signUp: PropTypes.func.isRequired,
}

const mapStateToProps = (state) => {
  return {
    auth: state.auth,
    user: state.fill.user,
    createdUser: state.user
  }
}

const mapDispatchToProps = {
  signUp: authActions.signUp,
  signOut: authActions.signOut,
  clearLastError: authActions.clearLastError,
  updateUser: updateUser,
  startFillData,
  saveChanges
}

export default withRouter(
  connect(mapStateToProps, mapDispatchToProps)(FillProfilePage)
)
