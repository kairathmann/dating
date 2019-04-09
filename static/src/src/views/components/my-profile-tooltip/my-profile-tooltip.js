import PropTypes from 'prop-types'
import React, { Component } from 'react'
import Img from 'react-image'
import ToolTip from 'react-portal-tooltip'
import { NavLink } from 'react-router-dom'
import Button from 'src/views/components/button'
import Icon from 'src/views/components/icon'
import './my-profile-tooltip.css'

class MyProfileTooltip extends Component {
  constructor (props) {
    super(props)
    this.state = {
      isTooltipActive: false,
    }
  }

  showTooltip = () => {
    this.setState({ isTooltipActive: true })
  }

  hideTooltip = () => {
    this.setState({ isTooltipActive: false })
  }

  render () {
    const { auth } = this.props
    if (auth && auth.authenticated) {
      return (
        <div className='my-profile-tooltip-container'
             onMouseEnter={ this.showTooltip }
             onMouseLeave={ this.hideTooltip }>
          { auth.photoURL ?
            <Img
              className='avatar'
              src={ this.props.auth.photoURL }/>
            :
            <span><Icon name='user'/></span>
          }

          <ToolTip active={ this.state.isTooltipActive } position='bottom' arrow='left'
                   parent='.my-profile-tooltip-container'>
            <span className='tooltip-container'>
              <NavLink to='/me'>My profile</NavLink><br/>
              <NavLink to='/messages'>Messages</NavLink><br/>
              <NavLink to='/findlove'>Find Love</NavLink><br/>
              <NavLink to='/deposit'>Deposit</NavLink><br/>
              <Button className='button-no-border' onClick={ this.props.signOut }>Disconnect</Button>
            </span>
          </ToolTip>
        </div>
      )
    } else {
      return (<span/>)
    }
  }
}

MyProfileTooltip.propTypes = {
  auth: PropTypes.object.isRequired,
  signOut: PropTypes.func.isRequired,
}

export default MyProfileTooltip
