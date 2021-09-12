import React from 'react';
import { Pagination } from '@material-ui/lab';
import { Avatar, Card, Chip, Grid, IconButton, List, ListItem, ListItemAvatar, ListItemSecondaryAction, ListItemText, Typography } from '@material-ui/core';
import { withStyles } from '@material-ui/core/styles';
import { Box } from '@material-ui/core';
import TimelineIcon from '@material-ui/icons/Timeline';
import CurvesListAPI from '../../helper/CurvesListAPI';
import DeleteIcon from '@material-ui/icons/Delete';
import EditIcon from '@material-ui/icons/Edit';

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
    this.api.history()
      .then(res => {
        return res.json()
      })
      .then(curves => {
        this.setState({
          curves: curves
        })
      })
      .catch(err => {
        console.log(err)
      });
  }

  render() {
    const { classes } = this.props;
    const { curves } = this.state;
    const handlePaginate = (e, page) => {
      this.api.history(page)
        .then(res => {
          return res.json()
        })
        .then(curves => {
          this.setState({
            curves: curves
          })
        })
        .catch(err => {
          console.log(err)
        });
    };
    if(curves) {
      return (
        <Box className={classes.root}>
          <Box m={2}>
            <Grid container>
              <Grid item xs={6}>
                <Typography component="h3">
                  履歴
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Pagination 
                  count={curves.pagination.total_pages}
                  variant="outlined" 
                  shape="rounded"
                  onChange={handlePaginate} />
              </Grid>
            </Grid>
            <List>
              {
                curves.models.map(curve => {
                  return <ListItem
                    key={curve.id}>
                    <ListItemAvatar>
                      <Avatar>
                        <TimelineIcon />
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText 
                      primary={ curve.content.title }
                      secondary={ curve.value_type.title }
                    />
                    <ListItemSecondaryAction>
                      <IconButton 
                        component="a" 
                        edge="end" 
                        aria-label="delete"
                        href={`/app/curves/${curve.id}`}>
                        <EditIcon />
                      </IconButton>
                      <IconButton 
                        edge="end" 
                        aria-label="delete"
                        onClick={_ => {
                          this.api.delete(curve.id, {
                            'format': 'json'
                          })
                          .then(res => {
                              if(res.status == 200) {
                                window.location.href = '/app/dashboard/';
                              }
                          });
                        }}>
                        <DeleteIcon />
                      </IconButton>
                    </ListItemSecondaryAction>
                  </ListItem>;
                })
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
