import { decorateConversation, decorateMessage } from './decorators'

describe('DECORATORS decorateConversation', () => {
  it('should process conversation', () => {
    const result = decorateConversation({
      partnerAvatarSmall: 'hydra/img/src/', partnerAvatarMedium: 'hydra/img/src/', partnerGender: 2
    })
    expect(result).toEqual({
      partnerGender: 2,
      avatarSmall: 'default_female',
      avatarMedium: 'default_female'
    })
  })
})

describe('DECORATORS decorateMessage', () => {
  it('should return processed message', () => {
    const result = decorateMessage({
      senderGender: 2, senderAvatar: 'hydra/img/src/'
    })
    expect(result).toEqual({
      senderGender: 2,
      avatarSmall: 'default_female'
    })
  })
})
