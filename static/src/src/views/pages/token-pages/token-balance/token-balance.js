import React from 'react'
import { injectIntl } from 'react-intl'
import { Link } from 'react-router-dom'

import { srcByRetina } from 'src/common/utils'

import deposit1 from 'src/images/deposit.png'
import deposit2 from 'src/images/deposit@2x.png'
import deposit3 from 'src/images/deposit@3x.png'

import withdraw1 from 'src/images/withdraw.png'
import withdraw2 from 'src/images/withdraw@2x.png'
import withdraw3 from 'src/images/withdraw@3x.png'

import routes, { toPath } from 'src/routes'
import TokenHeader from '../token-pages-header'

import './token-balance.css'

function TokenBalance ({intl}) {

  function renderTokenButton (actionName, iconSrc, path) {
    return (
      <Link className="token-btn" to={ path }>
        <img className='token-btn-img' src={ iconSrc } alt={ actionName }/>
        <div className="text semi-thin">{ actionName } Stars</div>
      </Link>
    )
  }

  return (
    <div className="token-balance-page">
      <TokenHeader
        openedTokenCount
        avatarTitle
        backPath={ toPath(routes.me) }
      />

      <div className="token-balance-body">
        { renderTokenButton(
          intl.formatMessage({id: 'balance.deposit'}),
          srcByRetina(deposit1, deposit2, deposit3),
          toPath(routes.deposit)
        ) }

        { renderTokenButton(
          intl.formatMessage({id: 'balance.withdraw'}),
          srcByRetina(withdraw1, withdraw2, withdraw3),
          toPath(routes.withdraw)
        ) }
      </div>
    </div>
  )

}

export default injectIntl(TokenBalance)
