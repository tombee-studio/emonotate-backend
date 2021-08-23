import React from 'react';
import Box from '@material-ui/core/Box';
import ContentsList from '../components/dashboard/ContentsList';
import { Divider } from '@material-ui/core';
import AddContent from '../components/content-list-page/AddContent';
import ContentsListAPI from '../helper/dashboard/ContentsListAPI';

export default function Dashboard(props) {
  const postAPI = new ContentsListAPI();

  return (
    <Box m={2}>
      <AddContent postAPI={data => {
        postAPI.post(data)
          .then(res => {
            return res.json();
          })
          .then(d => {
            console.log(d);
          });
      }} />
      <Divider />
      <Box m={1}>
        <ContentsList />
      </Box>
    </Box>
  );
}
