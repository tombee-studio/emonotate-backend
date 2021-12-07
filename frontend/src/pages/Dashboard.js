import React from 'react';
import Box from '@mui/material/Box';
import SearchResultList from '../components/common/SearchResultList';
import { withStyles } from '@mui/styles';

const styles = (theme) => ({
  root: {
    width: '100%',
    backgroundColor: theme.palette.background.paper,
  },
  inline: {
    display: 'inline',
  },
});

const Dashboard = (props) => {
  const { classes, keyword } = props;
  return (
    <Box m={2}>
      <SearchResultList keyword={keyword} />
    </Box>
  );
}

export default withStyles(styles)(Dashboard);
