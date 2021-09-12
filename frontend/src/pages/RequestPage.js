import React, {useEffect, useState} from 'react';
import {Box, Card} from '@material-ui/core';
import RequestListComponent from '../components/request-page/RequestListComponent';
import RequireListComponent from '../components/request-page/RequireListComponent';
import RequestListAPI from '../helper/RequestListAPI';

export default function RequestPage(props) {
  const [request, setRequest] = useState([]);
  const [require, setRequire] = useState([]);
  useEffect(() => {
    const requestAPI = new RequestListAPI();
    const requireAPI = new RequestListAPI();
    Promise.all([
      new Promise(resolve => {
        return requestAPI.get({
          'format': 'json',
          'role': 'participant',
        })
        .then(json => {
          resolve(json.models);
        });
      }),
      new Promise(resolve => {
        return requireAPI.get({
          'format': 'json',
          'role': 'owner',
        })
        .then(json => {
          resolve(json.models);
        });
      })
    ])
    .then(values => {
      const [_requests, _requires] = values;
      setRequest(_requests);
      setRequire(_requires);
    });
  }, []);
  return (
    <Box m={2}>
        <Card m={2}>
            <RequestListComponent requests={request} />
            <RequireListComponent requires={require} />
        </Card>
    </Box>
  );
}