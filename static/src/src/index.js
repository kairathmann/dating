import React from 'react'
import ReactDOM from 'react-dom'
import { IntlProvider } from 'react-intl'
import { Provider } from 'react-redux'
import { ConnectedRouter } from 'react-router-redux'
import configureApi from 'src/config/config'

import history from 'src/history'
import configureStore from 'src/store'
import App from 'src/views/app'
import 'src/views/styles/shared.css'
import 'src/views/styles/styles.css'

import {addLocaleData} from 'react-intl';
import english from 'react-intl/locale-data/en'
import chinese from 'react-intl/locale-data/zh'
import koreanic from 'react-intl/locale-data/ko'
import polish from 'react-intl/locale-data/pl'

import moment from 'moment'
import 'moment/locale/en-gb'
import 'moment/locale/pl'

import englishMessages from './i18n/en'
import polishMessages from './i18n/pl'

const store = configureStore()
const rootElement = document.getElementById('root')
configureApi()

addLocaleData([...english, ...polish,...koreanic, ...chinese])
const locale = 'en'
const messages = {
  en: englishMessages,
  pl: polishMessages
}
moment.locale(locale)

function render (Component) {
  ReactDOM.render(
    <IntlProvider messages={messages[locale]} locale={locale}>
      <Provider store={ store }>
        <ConnectedRouter history={ history }>
          <div>
            <Component/>
          </div>
        </ConnectedRouter>
      </Provider>
    </IntlProvider>,
    rootElement
  )
}

if (module.hot) {
  module.hot.accept('./views/app', () => {
    render(require('./views/app').default)
  })
}

render(App)
