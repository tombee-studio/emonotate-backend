import React from 'react';
import { BrowserRouter as Router, Route, Redirect } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import CreateCurvePage from './pages/CreateCurvePage';

export default class App extends React.Component {
  render() {
    return (
      <Router>
        <Route exact path="/app/">
          {<Redirect to="/app/dashboard/" />}
        </Route>
        <Route exact path='/app/dashboard/' component={ Dashboard } />
        <Route exact path='/app/new/:id' component={ CreateCurvePage } />
      </Router>
    );
  }
}
