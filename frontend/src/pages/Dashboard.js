import React from 'react';
import Box from '@material-ui/core/Box';
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
      <SearchResultList keyword={keyword} />
    </Box>
  );
}

export default withStyles(styles)(Dashboard);
