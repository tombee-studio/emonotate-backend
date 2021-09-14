import React from "react";
import { Box, Grid, List, ListItem } from "@material-ui/core";
import { Chart } from 'react-charts';
import videojs from 'video.js';
import "video.js/dist/video-js.css";

class ObserverComponent extends React.Component {
    constructor(props) {
        super(props);
        const { request } = this.props;
        this.request = request;
        this.CONSTANT = {
            video: 'video',
            chart: 'chart',
        };

        this.videoJsOptions = {
            autoplay: false,
            controls: true,
            sources: [{
                src:  request.content.url,
                type: request.content.data_type
            }]
        }

        this.state = {
            data: [
                {
                  label: 'abcde',
                  data: [[0, 1], [1, 2], [2, 4], [3, 2], [4, 7]]
                },
                {
                  label: 'bcdef',
                  data: [[0, 3], [1, 1], [2, 5], [3, 6], [4, 4]]
                }
            ],
            axes: [
                { primary: true, type: 'linear', position: 'bottom' },
                { type: 'linear', position: 'left' }
            ],
            users: [
                {
                    'id': 'abcde',
                    'data': {
                        'id': 'abcde',
                        'email': 'abc@abc.xyz.com',
                        'login': true,
                        'state': 'watching',
                    }
                },
                {
                    'id': 'bcdef',
                    'data': {
                        'id': 'bcdef',
                        'email': 'abc@abc.xyz.com',
                        'login': true,
                        'state': 'watching',
                    }
                }
            ]
        }
    }

    componentDidMount() {
        console.log('Connectinng..');
        this.socket = new WebSocket(`ws://${window.location.host}/ws/${this.request.room_name}/`);
        this.socket.onmessage = (e) => {
            alert(e.data);
        }

        this.player = videojs(this.videoNode, this.videoJsOptions);

        setInterval(() => {
            this.updateUserState({
                curve: [0, 1, 2, 3, 4].map(i => [i, Math.random() * 10]),
                user: {
                    'id': 'abcde',
                    'email': 'abc@abc.xyz.com',
                    'state': 'hey!',
                    'login': true,
                }
            });
        }, 5000);
    }

    updateUserState(userState) {
        const { curve, user } = userState;
        const curveData = this.state.data.concat();
        const userData = this.state.users.concat();
        const itemIndex = curveData.findIndex(item => item.label == user.id);
        const userIndex = userData.findIndex(item => item.id == user.id);
        curveData[itemIndex].data = curve;
        userData[userIndex].data = user;
        this.setState({
            data: curveData,
            users: userData
        });
    }

    render() {
        return (
            <div>
                <Box m={2}>
                    <Grid container>
                        <Grid item xs={5}>
                        <div data-vjs-player>
                            <video
                                id={ this.CONSTANT.video }
                                ref={ node => this.videoNode = node }
                                height={ 240 }
                                className="video-js" />
                        </div>
                        </Grid>
                        <Grid item xs={7}>
                            <div
                                style={{
                                    width: '100%',
                                    height: '100%'
                                }}>
                                <Chart data={this.state.data} axes={this.state.axes} />
                            </div>
                        </Grid>
                        <Grid item xs={12}>
                            <List>
                                { this.state.users.map(user => {
                                    return <ListItem key={user.id}>{ user.id }</ListItem>
                                })}
                            </List>
                        </Grid>
                    </Grid>
                </Box>
            </div>
        );
    }
};

export default ObserverComponent;
