import React from 'react';
import { BrowserRouter as Router, Route, Redirect } from 'react-router-dom';
import Dashboard from './pages/Dashboard';

export default class App extends React.Component {
  constructor(props) {
    super(props);

    this.state = {};
  }

  render() {
    return (
      <Router>
        <Route exact path="/app/">
          {<Redirect to="/app/dashboard/" />}
        </Route>
        <Route exact path='/app/dashboard/' render={() => <Dashboard {...this.state} />}  />
      </Router>
    );
  }
}
