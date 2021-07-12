import React from 'react';
import { Pagination } from '@material-ui/lab';
import { Card, Divider, Grid } from '@material-ui/core';
import { withStyles } from '@material-ui/core/styles';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import { Box } from '@material-ui/core';
import ListItemText from '@material-ui/core/ListItemText';
import ListItemAvatar from '@material-ui/core/ListItemAvatar';
import Avatar from '@material-ui/core/Avatar';
import Typography from '@material-ui/core/Typography';
import ContentsListAPI from '../../helper/dashboard/ContentsListAPI';

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
    this.api = new ContentsListAPI();
  }

  componentDidMount() {
    this.api.call(
      contents => {
        this.setState({
          contents: contents
        });
      },
      err => {
        throw err;
      });
  }

  render() {
    const { classes } = this.props;
    const { contents } = this.state;
    const handlePaginate = (e, page) => {
      this.api.call(
        contents => {
          this.setState({
            contents: contents
          });
        },
        err => {
          throw err;
        },
        page);
    };
    if(contents) {
      return (
        <Card>
          <Box m={2}>
            <Grid container>
              <Grid item xs={3}>
                <Typography component="h5" variant="h5">
                  動画
                </Typography>
              </Grid>
              <Grid item xs={6} />
              <Grid item 
                style={{ flexGrow: 0 }} 
                xs={3}>
                <Pagination 
                  count={contents.pagination.total_pages}
                  variant="outlined" 
                  shape="rounded"
                  onChange={handlePaginate} />
              </Grid>
            </Grid>
          </Box>
          <Divider />
          <List className={classes.root}>
            {
              contents.models.map(content => (
                <ListItem alignItems="flex-start"
                  button
                  key={content.id} 
                  component="a" 
                  href={'/app/new/' + content.id}>
                  <ListItemAvatar>
                    <Avatar alt={content.title} />
                  </ListItemAvatar>
                  <ListItemText
                    primary={content.title}
                    secondary={
                      <React.Fragment>
                        <Typography
                          component="span"
                          variant="body2"
                          className={classes.inline}
                          color="textPrimary"
                        >
                          {content.title}
                        </Typography>
                      </React.Fragment>
                    }
                  />
                </ListItem>
              ))
            }
          </List>
        </Card>
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
