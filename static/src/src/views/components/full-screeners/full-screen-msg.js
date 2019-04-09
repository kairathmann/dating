import PropTypes from 'prop-types'
import React from 'react'
import FullScreenContainer from './full-screen-container'

import './full-screen-msg.css'

export default function Loader ({ text }) {
  return (
    <FullScreenContainer>
      <div className="full-screen-msg text white x-bold">
        { text }
      </div>
    </FullScreenContainer>
  )
}

Loader.propTypes = {
  text: PropTypes.string.isRequired,
}
