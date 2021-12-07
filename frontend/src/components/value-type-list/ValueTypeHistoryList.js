import React from 'react';
import { Pagination } from '@mui/material';
import { Avatar, Card, IconButton, List, ListItem, ListItemAvatar, ListItemSecondaryAction, ListItemText } from '@mui/material';
import withStyles from '@mui/styles/withStyles';
import { Box } from '@mui/material';
import TextFormatIcon from '@mui/icons-material/TextFormat';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
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
                <ListItem button component="a">
                  <ListItemAvatar>
                    <Avatar>
                      <TextFormatIcon />
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText
                    key={item.id}
                    primary={item.title}
                    secondary={item.axis_type == 1 ? "対義語あり" :　"対義語なし"}
                  />
                  <ListItemSecondaryAction>
                    <IconButton
                      component="a"
                      href={`/app/valuetypes/${item.id}`}
                      edge="end"
                      aria-label="enter"
                      size="large">
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      component="a"
                      edge="end"
                      aria-label="delete"
                      onClick={_ => {
                        this.api.delete(item.id, {
                          'format': 'json'
                        })
                        .then(res => {
                            if(res.status == 200) {
                              window.location.href = '/app/word/';
                            }
                        });
                      }}
                      size="large">
                      <DeleteIcon />
                    </IconButton>
                  </ListItemSecondaryAction>
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
}

export default withStyles(styles)(UsersList);
