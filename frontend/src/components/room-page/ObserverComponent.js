import React from "react";
import { 
    Avatar, 
    Box, 
    Grid, 
    List, 
    ListItem, 
    ListItemAvatar, 
    ListItemText,
    Button } from "@material-ui/core";
import { Chart } from "react-charts";
import PersonIcon from "@material-ui/icons/Person";
import videojs from "video.js";
import "video.js/dist/video-js.css";
import CurvesListAPI from "../../helper/CurvesListAPI";

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
            data: request.participants.map(user => {
                return {
                    'label': user.id,
                    'data': []
                }
            }),
            axes: request.participants.map((_, i) => {
                if(i == 0) {
                    return { primary: true, type: 'linear', position: 'bottom' };
                } else {
                    return { type: 'linear', position: 'left' };
                }
            }),
            users: request.participants.map(user => {
                return {
                    'id': user.id,
                    'data': user,
                };
            })
        };
    }

    download(exportJson) {
        const fileName = 'finename.json';
        const data = new Blob([JSON.stringify(exportJson)], { type: 'text/json' });
        const jsonURL = window.URL.createObjectURL(data);
        const link = document.createElement('a');
        document.body.appendChild(link);
        link.href = jsonURL;
        link.setAttribute('download', fileName);
        link.click();
        document.body.removeChild(link);
    }

    componentDidMount() {
        this.player = videojs(this.videoNode, this.videoJsOptions);
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
                                    return <ListItem key={user.id}>
                                        <ListItemAvatar>
                                            <Avatar>
                                                <PersonIcon />
                                            </Avatar>
                                        </ListItemAvatar>
                                        <ListItemText
                                            primary={user.data.email}
                                        />
                                    </ListItem>
                                })}
                            </List>
                        </Grid>
                        <Grid item xs={12}>
                            <Grid container>
                                <Grid item xs={3}>
                                    <Button onClick={ev => {
                                        const api = new CurvesListAPI();
                                        api.list({
                                            'format': 'json',
                                            'search': this.request.room_name,
                                        })
                                        .then(json => {
                                            this.download(json);
                                            alert("ダウンロードを終了しました");
                                        })
                                        .catch(err => {
                                            alert(err);
                                        });
                                    }}>Download</Button>
                                </Grid>
                            </Grid>
                        </Grid>
                    </Grid>
                </Box>
            </div>
        );
    }
};

export default ObserverComponent;
