import React from 'react'
import './container.css'

export default function FullScreenContainer (props) {
  return (
    <div className="full-screen-container">
      { props.children }
    </div>
  )
}

FullScreenContainer.propTypes = {}
