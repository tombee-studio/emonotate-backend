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
    Divider } from '@material-ui/core';
import DeleteIcon from '@material-ui/icons/Delete';
import MeetingRoomIcon from '@material-ui/icons/MeetingRoom';
import EditIcon from '@material-ui/icons/Edit';
import RequestListAPI from '../../helper/RequestListAPI';

export default class RequireListComponent extends React.Component {
    constructor(props) {
        super(props);
        this.api = new RequestListAPI();
        this.state = {
            requests: []
        };
    }

    componentDidMount() {
        this.api.get({
            'format': 'json',
            'role': 'owner',
        })
        .then(json => {
            this.setState({
                requests: json.models,
            });
        });
    }

    render() {
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
                        this.state.requests.map(request => {
                            return (
                                <ListItem
                                    button
                                    component="a"
                                    href={`/app/room/${request.id}`}
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
                                            aria-label="enter">
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
                                                        if(res.status == 200) {
                                                            window.location.href = '/app/request';
                                                        }
                                                    });
                                            }}>
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
