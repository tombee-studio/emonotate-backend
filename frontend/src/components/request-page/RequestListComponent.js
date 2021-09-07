import React from 'react';
import { List, ListItem, ListItemText, Box, Typography } from '@material-ui/core';
import RequestListAPI from '../../helper/RequestListAPI';

export default class RequestListComponent extends React.Component {
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
            'role': 'participant',
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
                <List>
                    {
                        this.state.requests.map(request => {
                            return (
                                <ListItem
                                    button
                                    component="a"
                                    href={`/app/new/?content=${request.content.id}&value_type=${request.value_type.id}`}
                                    key={request.room_name}
                                    alignItems="flex-start">
                                    <ListItemText
                                    primary={request.title}
                                    secondary={
                                        <React.Fragment>
                                            <Typography
                                                component="span"
                                                variant="body2"
                                                color="textPrimary"
                                            >
                                                { request.owner.email }
                                            </Typography> <br />
                                            { request.description }
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
