import React from 'react'
import { Redirect, Route } from 'react-router-dom'
import routes, { toPath } from 'src/routes'

const RequireAuthRouteHOC = ({ auth, needAuth, component: Component, componentProps, render, ...rest }) => {
  const renderer = render || ((props) => (<Component { ...props } { ...componentProps }/>))
  const redirectRenderer = (props) => (<Redirect to={ {
    pathname: toPath(needAuth ? '' : routes.recommendations),
    state: { from: props.location },
  } }/>)

  const { authenticated } = auth
  return (

    <Route
      { ...rest }
      render={ props => {
        return (
          (needAuth && authenticated) || (!needAuth && !authenticated)) ? renderer(props) : redirectRenderer(props)
      } }
    />
  )
}

export const RequireAuthRoute = ({ component, authenticated, componentProps, render, ...rest }) => (
  RequireAuthRouteHOC({ needAuth: true, component, authenticated, componentProps, render, ...rest })
)

export const RequireUnauthRoute = ({ component, authenticated, componentProps, render, ...rest }) => (
  RequireAuthRouteHOC({ needAuth: false, component, authenticated, componentProps, render, ...rest })
)
