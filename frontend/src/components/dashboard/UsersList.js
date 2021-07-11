import React from 'react';
import { Pagination } from '@material-ui/lab';
import { Card } from '@material-ui/core';
import { withStyles } from '@material-ui/core/styles';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import { Box } from '@material-ui/core';
import ListItemText from '@material-ui/core/ListItemText';
import ListItemAvatar from '@material-ui/core/ListItemAvatar';
import Avatar from '@material-ui/core/Avatar';
import Typography from '@material-ui/core/Typography';

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
  }

  componentDidMount() {
    fetch('/api/users/?format=json')
      .then(res => res.json())
      .then(users => {
        this.setState({
          users: users
        });
      }); 
  }

  render() {
    const { classes } = this.props;
    const { users } = this.state;
    const handlePaginate = (e, page) => {
      fetch(`/api/users/?format=json&page=${page}`)
        .then(res => {
          return res.json();
        })
        .then(users => {
          this.setState({
            users: users
          });
        });
    };
    if(users) {
      return (
        <Card>
          <Box m={2}>
            <Pagination 
              count={users.pagination.total_pages} 
              variant="outlined" 
              shape="rounded"
              onChange={handlePaginate} />
            <List className={classes.root}>
              {
                users.models.map(user => (
                  <ListItem alignItems="flex-start" key={user.id}>
                    <ListItemAvatar>
                      <Avatar alt={user.first_name} />
                    </ListItemAvatar>
                    <ListItemText
                      primary={user.first_name + " " + user.last_name}
                      secondary={
                        <React.Fragment>
                          <Typography
                            component="span"
                            variant="body2"
                            className={classes.inline}
                            color="textPrimary"
                          >
                            {user.email}
                          </Typography>
                        </React.Fragment>
                      }
                    />
                  </ListItem>
                ))
              }
            </List>
          </Box>
        </Card>
      );
    } else {
      return (<Card />);
    }
  };
};

export default withStyles(styles)(UsersList);
