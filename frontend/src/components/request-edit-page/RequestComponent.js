import React from "react";
import { Box, Grid } from "@material-ui/core";
import videojs from 'video.js';
import Helmet from 'react-helmet';
import "video.js/dist/video-js.css";

class RequestComponent extends React.Component {
    constructor(props) {
        super(props);
        const { request } = this.props;
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
    }

    componentDidMount() {
        this.player = videojs(this.videoNode, this.videoJsOptions);
    }

    render() {
        const { request } = this.props;
        console.log(request);
        return (
            <div>
                <Helmet>
                    <script src="/static/users/js/emotional-arc-input-field.js" />
                    <link rel="stylesheet" href="/static/users/css/emotional-arc-input-field.css" />
                    <script src="/static/users/d3/d3.min.js" />
                </Helmet>
                <Box m={2}>
                    <Grid container>
                        <Grid item xs={5}>
                        <div data-vjs-player>
                            <video
                                id={ this.CONSTANT.video }
                                ref={ node => this.videoNode = node }
                                height={ 120 }
                                className="video-js" />
                        </div>
                        </Grid>
                        <Grid item xs={12}>
                        </Grid>
                    </Grid>
                </Box>
            </div>
        );
    }
};

export default RequestComponent;