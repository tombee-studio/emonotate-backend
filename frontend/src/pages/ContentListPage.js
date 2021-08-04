import React from 'react';
import Box from '@material-ui/core/Box';
import ContentsList from '../components/dashboard/ContentsList';
import { Divider } from '@material-ui/core';
import AddContent from '../components/content-list-page/AddContent';

export default function Dashboard(props) {
  return (
    <Box m={2}>
      <AddContent />
      <Divider />
      <Box m={1}>
        <ContentsList />
      </Box>
    </Box>
  );
}
