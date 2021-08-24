import React from 'react';
import Box from '@material-ui/core/Box';
import { Divider } from '@material-ui/core';
import ValueTypeListAPI from '../helper/ValueTypeListAPI';
import ValueTypeHistoryList from '../components/value-type-list/ValueTypeHistoryList';
import AddValueType from '../components/value-type-list/AddValueType';

export default function Dashboard(props) {
  const postAPI = new ValueTypeListAPI();

  return (
    <Box m={2}>
      <AddValueType postAPI={data => {
        postAPI.post(data)
          .then(res => {
            return res.json();
          })
          .then(d => {
            window.location.href = '/';
          });
      }} />
      <Divider />
      <Box m={1}>
        <ValueTypeHistoryList />
      </Box>
    </Box>
  );
}
