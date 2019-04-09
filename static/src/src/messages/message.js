import { Record } from 'immutable'

export const Message = new Record({
  id: null,
  conversationId: null,
  createdAt: null,
  body: null,
  from: null,
  to: null,
})
