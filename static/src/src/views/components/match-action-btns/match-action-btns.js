import PropTypes from 'prop-types'
import React from 'react'
import Button from 'src/views/components/button'
import Icon from 'src/views/components/icon'
import './match-action-btns.css'

export default function MatchActionBtns ({ onReaction }) {
  return (
    <div className='match-action-btns'>
      <Button
        className='button-no-border close-btn'
        onClick={ () => {
          onReaction(false)
        } }
      >
        <Icon className='close-icon' name='close'/>
      </Button>
      <Button
        className='button-no-border message-btn'
        onClick={ () => {
          onReaction(true)
        } }
      >
        <Icon className='message-icon' name='mail_outline'/>
      </Button>
    </div>
  )
}

MatchActionBtns.propTypes = {
  onReaction: PropTypes.func.isRequired,
}
