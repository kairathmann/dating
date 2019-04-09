import { avatarUrlToPhotoUrlObj, rewriteUrlImageForDefault } from './utils'

export function decorateConversation ({ partnerAvatarSmall, partnerAvatarMedium, partnerGender, ...rest }) {
  const [ avatarSmall, avatarMedium ] = [ partnerAvatarSmall, partnerAvatarMedium ]
    .map(avatar => {
      const { photoURL } = avatarUrlToPhotoUrlObj(avatar)
      return rewriteUrlImageForDefault(photoURL, partnerGender)
    })
  return { ...rest, partnerGender, avatarSmall, avatarMedium }
}

export function decorateMessage ({ senderAvatar, senderGender, ...rest }) {
  const { photoURL } = avatarUrlToPhotoUrlObj(senderAvatar)
  const avatarSmall = rewriteUrlImageForDefault(photoURL, senderGender)
  return {
    ...rest,
    senderGender,
    avatarSmall
  }
}
