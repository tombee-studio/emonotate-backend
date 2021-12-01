import React from 'react';
import Box from '@material-ui/core/Box';
import Divider from '@material-ui/core/Divider';
import ContentsList from '../components/dashboard/ContentsList';
import History from '../components/dashboard/History';
import SearchResultList from '../components/common/SearchResultList';
import { withStyles } from '@material-ui/styles';

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
      <Box m={1} className={classes.root}>
        <SearchResultList keyword={keyword} />
      </Box>
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

export default withStyles(styles)(Dashboard);
