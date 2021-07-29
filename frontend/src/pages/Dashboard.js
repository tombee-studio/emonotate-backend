import React from 'react';
import Box from '@material-ui/core/Box';
import Divider from '@material-ui/core/Divider';
import ContentsList from '../components/dashboard/ContentsList';
import History from '../components/dashboard/History';

export default function Dashboard(props) {
  return (
    <Box m={2}>
      <Divider />
      <Box m={1}>
        <ContentsList />
      </Box>
      <Divider />
      <Box m={1}>
        <History />
      </Box>
    </Box>
  );
}