import React from 'react';
import Box from '@material-ui/core/Box';
import RequestListComponent from '../components/request-page/RequestListComponent';

export default function RequestPage(props) {
  return (
    <Box m={2}>
      <RequestListComponent />
    </Box>
  );
}