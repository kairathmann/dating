/**
 * @enum {ASYNC_STATES}
 */
export const ASYNC_STATES = {
  BEFORE: Symbol('before'),
  DURING: Symbol('during'),
  SUCCESS: Symbol('success'),
  FAIL: Symbol('fail'),
}

// todo: should be fetched from server
export const BID_STATUS = {
  BID_WINNING: 1,
  BID_LOSING: 2,
  BID_WON: 3,
  BID_LOST: 4,
  BID_ACCEPTED: 5,
  BID_TIMEOUT: 6,
}

export const GENDER = {
  // todo: should come from server

  MALE: 1,
  FEMALE: 2,
  OTHER: 3,
  BOTH: 3,
}

export const STATE = {
  INCOMPLETE: 1,
  ACTIVE: 2,
  DISABLED: 3,
  DELETED: 4
}

export const CONSTANTS = {
  MAX_AGE: 100,
  MIN_AGE: 18
}
