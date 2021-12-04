import React from 'react';
import { 
  BrowserRouter as Router, 
  Route, 
  Redirect, 
  Switch } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import Dashboard from './pages/Dashboard';
import HistoryPage from './pages/HistoryPage';
import ContentListPage from './pages/ContentListPage';
import ValueTypeListPage from './pages/ValueTypeListPage';
import RequestPage from './pages/RequestPage';
import RoomPage from './pages/RoomPage';
import ProfilePage from './pages/ProfilePage';
import CurvePage from './pages/CurvePage';

const App = () => {
  return (
    <Router>
      <MainLayout component={keyword => {
        return (<Switch>
          <Route exact path="/app/">
            {<Redirect to="/app/dashboard/" />}
          </Route>
          <Route exact path='/app/dashboard/' render={_ => <Dashboard keyword={keyword} />} />
          <Route exact path='/app/history/' component={ HistoryPage } />
          <Route exact path='/app/content/' component={ ContentListPage } />
          <Route exact path='/app/word/' component={ ValueTypeListPage } />
          <Route exact path='/app/curves/' render={ props => <CurvePage /> } />
          <Route path='/app/curves/:id(\d+)' component={ props => 
            <CurvePage id={props.match.params.id} /> 
          } />
          <Route exact path='/app/requests/' component={ RequestPage } />
          <Route exact path='/app/rooms/' component={ _ => 
            <RoomPage keyword={keyword} />
          } />
          <Route exact path='/app/rooms/:id(\d+)' component={ props => 
            <RoomPage id={props.match.params.id} keyword={keyword} />
          } />
          <Route exact path='/app/profile/' component={ ProfilePage } />
        </Switch>);
      }} />
    </Router>
  );
}

export default App;
