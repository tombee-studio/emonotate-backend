import React from 'react';
import { BrowserRouter as Router, Route, Redirect, Switch } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import Dashboard from './pages/Dashboard';
import CreateCurvePage from './pages/CreateCurvePage';
import HistoryPage from './pages/HistoryPage';

export default class App extends React.Component {
  render() {
    return (
      <Router>
        <MainLayout>
          <Switch>
            <Route exact path="/app/">
              {<Redirect to="/app/dashboard/" />}
            </Route>
            <Route exact path='/app/dashboard/' component={ Dashboard } />
            <Route exact path='/app/history/' component={ HistoryPage } />
            <Route exact path='/app/new/:id' component={ CreateCurvePage } />
          </Switch>
        </MainLayout>
      </Router>
    );
  }
}
