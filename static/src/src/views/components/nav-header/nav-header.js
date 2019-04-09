import React from 'react'
import Img from 'react-image'

import { srcByRetina } from 'src/common/utils'

import messagesImg from 'src/images/messages.png'
import messagesActiveImg from 'src/images/messages_active.png'
import navLunaActive from 'src/images/nav-icon-luna-active.png'
import navLunaActive2 from 'src/images/nav-icon-luna-active@2x.png'

import navLuna from 'src/images/nav-icon-luna.png'
import navLuna2 from 'src/images/nav-icon-luna@2x.png'

import profileImg from 'src/images/profile.png'
import profileActiveImg from 'src/images/profile_active.png'
import routes, { toPath } from 'src/routes'
import Header from 'src/views/components/header'
import Button from '../button'

import './nav-header.css'

const NavHeader = ({ history, activeRoute }) => (
  <Header className='nav-header'>
    <Button
      className='button-no-background button-info'
      onClick={ () => {
        history.push(toPath(routes.viewProfile))
      } }
    >
      <Img
        src={ (activeRoute === routes.viewProfile) ? profileImg : profileActiveImg }
        alt={ 'My profile' }
      />
    </Button>
    <Button
      className='button-no-background button-info luna-icon'
      onClick={ () => {
        history.push(toPath(routes.recommendations))
      } }>
      <Img
        src={ (activeRoute === routes.recommendations) ? srcByRetina(navLunaActive, navLunaActive2) : srcByRetina(
          navLuna,
          navLuna2) }
        alt={ 'Browse for love' }
      />
    </Button>
    <Button
      className='button-no-background button-info'
      onClick={ () => {
        history.push(toPath(routes.messages))
      } }
    >
      <Img
        src={ (activeRoute === routes.messages) ? messagesImg : messagesActiveImg }
        alt={ 'My messages' }
      />
    </Button>
  </Header>
)

export default NavHeader
