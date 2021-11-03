import React from 'react';
import { BrowserRouter as Router, Route, Redirect, Switch } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import Dashboard from './pages/Dashboard';
import HistoryPage from './pages/HistoryPage';
import ContentListPage from './pages/ContentListPage';
import ValueTypeListPage from './pages/ValueTypeListPage';
import RequestPage from './pages/RequestPage';
import RoomPage from './pages/RoomPage';
import RequestEditPage from './pages/RequestEditPage';
import CurveEditPage from './pages/CurveEditPage';
import ProfilePage from './pages/ProfilePage';
import CreateCurvePage from './pages/CreateCurvePage';
import CreateRequestPage from './pages/CreateRequestPage';

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
            <Route exact path='/app/content/' component={ ContentListPage } />
            <Route exact path='/app/word/' component={ ValueTypeListPage } />
            <Route exact path='/app/new/:name' component={ props => {
              const { name } = props.match.params;
              if(name == 'curve') return <CreateCurvePage />;
              else if(name == 'request') return <CreateRequestPage />;
              else <div />;
            } } />
            <Route path='/app/curves/:id(\d+)' component={ props => 
              <CurveEditPage id={props.match.params.id} /> 
            } />
            <Route exact path='/app/requests/' component={ RequestPage } />
            <Route path='/app/requests/:id(\d+)' component={ props => 
              <RequestEditPage id={props.match.params.id} /> 
            } />
            <Route exact path='/app/rooms/:id(\d+)' component={ props => 
              <RoomPage id={props.match.params.id} /> 
            } />
            <Route exact path='/app/profile/' component={ ProfilePage } />
          </Switch>
        </MainLayout>
      </Router>
    );
  }
}
