import React from 'react';
import Box from '@material-ui/core/Box';
import Typography from '@material-ui/core/Typography';
import Divider from '@material-ui/core/Divider';
import Link from '@material-ui/core/Link';
import ContentsList from '../components/dashboard/ContentsList';

export default function Dashboard(props) {
  return (
    <Box m={2}>
      <Divider />
      <Box m={1}>
        <ContentsList />
      </Box>
    </Box>
  );
}