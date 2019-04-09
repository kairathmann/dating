import classnames from 'classnames'
import PropTypes from 'prop-types'
import React from 'react'
import { FormattedMessage } from 'react-intl'

import { connect } from 'react-redux'
import { AvatarRound, BackButton, Header, HeaderTitle, StarIcon } from 'src/views/components'

import './token-page-header.css'

function renderHeader ({ backPath, avatarTitle, user, title }) {
  return (
    <Header key='header' equalSidesForStrictCenter>
      <BackButton destination={ backPath }/>
      { avatarTitle ? (
        <AvatarRound
          photoURL={ user.photoURL }
          imgClass={ 'avatar' }
          sizeInRem={ 3.67 }
          alt='user avatar'
        />
      ) : (
        <HeaderTitle title={ title }/>
      )
      }
      <span/> { /* for layout = left | middle | fake-right */ }
    </Header>
  )
}

function renderTokenCount ({ token, openedTokenCount }) {

  return (
    <div key='count' className={ classnames('token-header', openedTokenCount ? 'opened' : 'closed') }>
      { openedTokenCount ?
        (
          [
            <div key={ 1 } className="token-count-title text small semi-thin"><FormattedMessage id={'token.manage_balance'}/></div>,
            <div key={ 2 } className="token-count-body">
              <StarIcon/>
              <span className="token-amount">{ token.confirmedBalance || 0 }</span>
              <span className="ico-name text small semi-thin">LSTR</span>
            </div>
          ]
        ) : (
          [
            <span key={ 1 }>{ token.confirmedBalance }</span>,
            <StarIcon key={ 2 }/>
          ]
        ) }

    </div>
  )
}

function TokenPageCommonHeader ({ user, token, title, backPath, avatarTitle, openedTokenCount = false }) {
  return (
    [
      renderHeader({ backPath, avatarTitle, user, title }),
      renderTokenCount({ token, openedTokenCount })
    ]
  )
}

TokenPageCommonHeader.propTypes = {
  token: PropTypes.shape({
    confirmedBalance: PropTypes.number,
    unconfirmedBalance: PropTypes.number,
  }).isRequired,

  avatarTitle: PropTypes.bool,
  title: PropTypes.string, // required if avatarTitle === false
  backPath: PropTypes.string.isRequired, // path from routes.
  openedTokenCount: PropTypes.bool
}

const mapStateToProps = (state) => {
  return {
    token: state.token,
    user: state.user
  }
}

export default connect(
  mapStateToProps,
)(TokenPageCommonHeader)
