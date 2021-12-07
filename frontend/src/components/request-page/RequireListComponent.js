import React from 'react';
import { 
    List, 
    ListItem, 
    ListItemText, 
    ListItemSecondaryAction,
    ListItemAvatar,
    IconButton,
    Avatar,
    Box, 
    Typography, 
    Divider } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import MeetingRoomIcon from '@mui/icons-material/MeetingRoom';
import EditIcon from '@mui/icons-material/Edit';
import RequestListAPI from '../../helper/RequestListAPI';

export default class RequireListComponent extends React.Component {
    constructor(props) {
        super(props);
        this.api = new RequestListAPI();
    }

    render() {
        const { requires } = this.props;
        return (
            <Box m={2}>
                <Typography
                    component="span"
                    variant="h6"
                    color="textPrimary"
                >
                    あなたが設定した実験
                </Typography>
                <Divider />
                <List>
                    {
                        requires.map(request => {
                            return (
                                <ListItem
                                    button
                                    component="a"
                                    href={`/app/rooms/${request.id}`}
                                    key={request.room_name}>
                                    <ListItemAvatar>
                                        <Avatar>
                                            <MeetingRoomIcon />
                                        </Avatar>
                                    </ListItemAvatar>
                                    <ListItemText
                                        primary={request.title}
                                        secondary={
                                            request.description.length > 30?
                                            request.description.substr(0, 30) + "...":
                                            request.description
                                        }
                                    />
                                    <ListItemSecondaryAction>
                                        <IconButton
                                            component="a"
                                            href={`/app/requests/${request.id}`}
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
                                                this.api.delete(request.id, {
                                                    'format': 'json'
                                                })
                                                .then(res => {
                                                    if(res.status == 200 || res.status == 204) {
                                                        window.location.href = '/app/requests/';
                                                    }
                                                });
                                            }}
                                            size="large">
                                            <DeleteIcon />
                                        </IconButton>
                                    </ListItemSecondaryAction>
                                </ListItem>
                            );
                        })
                    }
                </List>
            </Box>
        );
    }
};
