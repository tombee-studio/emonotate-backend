import React from 'react';
import { 
    List, 
    ListItem, 
    ListItemText, 
    Box, 
    Typography, 
    Divider,
    ListItemAvatar,
    Avatar } from '@material-ui/core';
import MailIcon from '@material-ui/icons/Mail';

export default class RequestListComponent extends React.Component {
    render() {
        const { requests } = this.props;
        return (
            <Box m={2}>
                <Typography
                    component="span"
                    variant="h6"
                    color="textPrimary"
                >
                    あなたへの依頼
                </Typography>
                <Divider />
                <List>
                    {
                        requests.map(request => {
                            return (
                                <ListItem
                                    button
                                    component="a"
                                    href={
                                        `/app/new/?content=${request.content.id}&value_type=${request.value_type.id}&room=${request.room_name}`
                                    }
                                    key={request.room_name}
                                    alignItems="flex-start">
                                    <ListItemAvatar>
                                        <Avatar>
                                            <MailIcon />
                                        </Avatar>
                                    </ListItemAvatar>
                                    <ListItemText
                                    primary={<React.Fragment>
                                        <Typography
                                            component="span"
                                            color="textPrimary"
                                        >
                                            { 
                                                request.title
                                            }
                                        </Typography>
                                        <Typography
                                            component="span"
                                            variant="subtitle1"
                                            color="textSecondary"
                                        >
                                            { 
                                                ` from ${request.owner.email}`
                                            }
                                        </Typography>
                                    </React.Fragment>}
                                    secondary={
                                        <React.Fragment>
                                            <Typography
                                                component="span"
                                                variant="body2"
                                                color="textSecondary"
                                            >
                                                { 
                                                    request.description.length > 30?
                                                    request.description.substr(0, 30) + "...":
                                                    request.description
                                                }
                                            </Typography>
                                        </React.Fragment>
                                    }
                                    />
                                </ListItem>
                            );
                        })
                    }
                </List>
            </Box>
        );
    }
};
