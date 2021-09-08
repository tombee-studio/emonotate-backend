import React from 'react';
import {Box, Card} from '@material-ui/core';
import RequestListComponent from '../components/request-page/RequestListComponent';
import RequireListComponent from '../components/request-page/RequireListComponent';

export default function RequestPage(props) {
  return (
    <Box m={2}>
        <Card m={2}>
            <RequestListComponent />
            <RequireListComponent />
        </Card>
    </Box>
  );
}