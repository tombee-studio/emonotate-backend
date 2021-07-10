import React from 'react';
import { BrowserRouter as Router, Route, Redirect } from 'react-router-dom';
import Dashboard from './pages/Dashboard';

export default class App extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      users: {
        "pagination": {
            "previous_page": null,
            "next_page": 2,
            "start_index": 1,
            "end_index": 10,
            "total_entries": 101,
            "total_pages": 11,
            "page": 1
        },
        "models": [
          {
              "id": 1,
              "first_name": "Voluptat",
              "last_name": "Est quia reru",
              "email": "jtfabeayfouotpflpcmcdsfc@i.hzw",
              "last_login": "2022-07-04T22:35:42.529912Z",
              "is_active": true,
              "date_joined": "2021-07-07T09:28:20.528915Z",
              "last_updated": "2021-07-07T09:28:20.533711Z"
          },
          {
              "id": 2,
              "first_name": "Consectetur recusand",
              "last_name": "Incid",
              "email": "rp@gnswaeyknusmogjvupzrwcj.ssp",
              "last_login": "2021-09-02T14:00:05.529912Z",
              "is_active": true,
              "date_joined": "2021-07-07T09:28:20.547132Z",
              "last_updated": "2021-07-07T09:28:20.547959Z"
          },
          {
              "id": 3,
              "first_name": "Inventore earum n",
              "last_name": "Beatae veniam d",
              "email": "iapdphtztenlwrkvg@utdc.odn",
              "last_login": "2022-03-20T05:37:50.529912Z",
              "is_active": true,
              "date_joined": "2021-07-07T09:28:20.551625Z",
              "last_updated": "2021-07-07T09:28:20.552625Z"
          },
          {
              "id": 4,
              "first_name": "Quae dolorem neque",
              "last_name": "Ipsa quo autem ullam nihil e",
              "email": "gvq@jaxtopovaj.wuk",
              "last_login": "2017-12-23T08:02:54.529912Z",
              "is_active": true,
              "date_joined": "2021-07-07T09:28:20.556681Z",
              "last_updated": "2021-07-07T09:28:20.557499Z"
          },
          {
              "id": 5,
              "first_name": "Quod temporib",
              "last_name": "Molestias dolorem",
              "email": "qrpuiorgcchlziklnh@jbl.eko",
              "last_login": null,
              "is_active": true,
              "date_joined": "2021-07-07T09:28:20.560862Z",
              "last_updated": "2021-07-07T09:28:20.561860Z"
          },
          {
              "id": 6,
              "first_name": "Ea labore impedit atque, tenet",
              "last_name": "Deserunt omnis",
              "email": "jbfpel@qkf.ljv",
              "last_login": null,
              "is_active": true,
              "date_joined": "2021-07-07T09:28:20.566333Z",
              "last_updated": "2021-07-07T09:28:20.567330Z"
          },
          {
              "id": 7,
              "first_name": "Ea est autem voluptatum",
              "last_name": "Ut eaque",
              "email": "xbdgglehditorspfyzj@l.qgi",
              "last_login": null,
              "is_active": true,
              "date_joined": "2021-07-07T09:28:20.570868Z",
              "last_updated": "2021-07-07T09:28:20.570868Z"
          },
          {
              "id": 8,
              "first_name": "Repellat vita",
              "last_name": "Voluptatibus atq",
              "email": "oee@rbctxhakyndfstmcbk.skn",
              "last_login": "2021-05-31T17:48:29.529912Z",
              "is_active": true,
              "date_joined": "2021-07-07T09:28:20.575557Z",
              "last_updated": "2021-07-07T09:28:20.576556Z"
          },
          {
              "id": 9,
              "first_name": "Earum saepe accusamus dignissi",
              "last_name": "Laudantium in quas sunt delen",
              "email": "weu@fdbsjyrfqidwiqcjljyec.udt",
              "last_login": "2019-11-18T09:45:25.529912Z",
              "is_active": true,
              "date_joined": "2021-07-07T09:28:20.579825Z",
              "last_updated": "2021-07-07T09:28:20.580857Z"
          },
          {
              "id": 10,
              "first_name": "Itaque quidem quis magn",
              "last_name": "Accusamus ratione aspernat",
              "email": "nsyauhjqpdkkdaoqlctz@tbebq.bqs",
              "last_login": "2018-04-21T22:57:31.529912Z",
              "is_active": true,
              "date_joined": "2021-07-07T09:28:20.584811Z",
              "last_updated": "2021-07-07T09:28:20.585809Z"
          }
        ]
      }
    };
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
