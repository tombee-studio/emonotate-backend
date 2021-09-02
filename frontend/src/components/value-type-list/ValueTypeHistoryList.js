import React from 'react';
import { Pagination } from '@material-ui/lab';
import { Card, List, ListItem, ListItemText } from '@material-ui/core';
import { withStyles } from '@material-ui/core/styles';
import { Box } from '@material-ui/core';
import ValueTypeListAPI from '../../helper/ValueTypeListAPI';

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
    this.api = new ValueTypeListAPI();
  }

  componentDidMount() {
    this.api.history(
      valuetypes => {
        this.setState({
          valuetypes: valuetypes
        });
      },
      err => {
        throw err;
      });
  }

  render() {
    const { classes } = this.props;
    const { valuetypes } = this.state;
    const handlePaginate = (e, page) => {
      this.api.history(
        valuetypes => {
          this.setState({
            valuetypes: valuetypes
          });
        },
        err => {
          throw err;
        },
        page);
    };

    const generate = (data, element) => {
      return data.map((value) =>
        React.cloneElement(element, {
          id: value.id,
          primary: value.title,
          secondary: value.title,
        }),
      );
    };

    if(valuetypes) {
      return (
        <Box className={classes.root}>
          <Box m={2}>
            <Pagination 
              count={valuetypes.pagination.total_pages}
              variant="outlined" 
              shape="rounded"
              onChange={handlePaginate} />
          </Box>
          <Box m={2}>
          <List>
            {
              valuetypes.models.map(item => (
                <ListItem button>
                  <ListItemText
                    key={item.id}
                    primary={item.title}
                    secondary={item.axis_type == 1 ? "対義語あり" :　"対義語なし"}
                  />
                </ListItem>
              ))
            }
            </List>
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
