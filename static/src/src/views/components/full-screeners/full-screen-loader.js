import React from 'react'
import LunaLoader from 'src/views/components/loaders/luna-loader'

import FullScreenContainer from './full-screen-container'

import './full-screen-loader.css'

export default function Loader () {
  return (
    <FullScreenContainer>
      <LunaLoader color={ 'white' } sizeInRem={ 5 }/>
    </FullScreenContainer>
  )
}

Loader.propTypes = {}
