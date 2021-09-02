import React from 'react';
import Box from '@material-ui/core/Box';
import History from '../components/dashboard/History';

export default function HistoryPage(props) {
  return (
    <Box m={2}>
      <Box m={1}>
        <History />
      </Box>
    </Box>
  );
}