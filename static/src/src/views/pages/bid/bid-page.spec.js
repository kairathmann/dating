import Enzyme, { shallow } from 'enzyme'
import Adapter from 'enzyme-adapter-react-16'
import React from 'react'
import { IntlProvider } from 'react-intl'
import configureMockStore from 'redux-mock-store'
import { BidPage } from './bid-page'
import messages from '../../../i18n/en'

Enzyme.configure({ adapter: new Adapter() })

function setup (overridenProps) {
  const intlProvider = new IntlProvider({ locale: 'en', messages }, {})
  const { intl } = intlProvider.getChildContext()

  const props = {
    auth: {},
    targetUser: {},
    createConversation: jest.fn(),
    token: {
      confirmedBalance: 0,
      unconfirmedBalance: 0,
    },
    intl,
    store: configureMockStore({}),
    ...overridenProps
  }

  const enzymeWrapper = shallow(<BidPage { ...props } />, { context: { intl } })

  return {
    props,
    enzymeWrapper
  }
}

describe('BidPage', () => {
  describe('likely', () => {
    it('should return 1 if minBid = 0', () => {
      const { enzymeWrapper } = setup({ targetUser: { minBid: 0, photoURL: '' } })
      const result = enzymeWrapper.instance().likely
      expect(result).toEqual(1)
    })

    it('should return 2 if minBid = 2', () => {
      const { enzymeWrapper } = setup({ targetUser: { minBid: 2, photoURL: '' } })
      const result = enzymeWrapper.instance().likely
      expect(result).toEqual(2)
    })
  })
})
