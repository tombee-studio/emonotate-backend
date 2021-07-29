import React from 'react';
import { Pagination } from '@material-ui/lab';
import { Card, List, ListItem } from '@material-ui/core';
import { withStyles } from '@material-ui/core/styles';
import { Box } from '@material-ui/core';
import CurvesListAPI from '../../helper/dashboard/CurvesListAPI';

const styles = (theme) => ({
  root: {
    width: '100%',
    backgroundColor: theme.palette.background.paper,
  },
  inline: {
    display: 'inline',
  },
});

class UsersList extends React.Component {
  constructor(props) {
    super(props);

    this.state = {};
    this.api = new CurvesListAPI();
  }

  componentDidMount() {
    this.api.call(
      curves => {
        this.setState({
          curves: curves
        });
      },
      err => {
        throw err;
      });
  }

  render() {
    const { classes } = this.props;
    const { curves } = this.state;
    const handlePaginate = (e, page) => {
      this.api.call(
        curves => {
          this.setState({
            curves: curves
          });
        },
        err => {
          throw err;
        },
        page);
    };
    if(curves) {
      return (
        <Box className={classes.root}>
          <Box m={2}>
            <Pagination 
              count={curves.pagination.total_pages}
              variant="outlined" 
              shape="rounded"
              onChange={handlePaginate} />
          </Box>
        </Box>
      );
    } else {
      return (
        <Card>
          <Box>
            LOAD DATA...
          </Box>
        </Card>
      );
    }
  };
};

export default withStyles(styles)(UsersList);
