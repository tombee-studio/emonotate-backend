import React from "react";

import { 
    Box,
    Grid,
} from "@mui/material";

import { useState } from "react";
import { useLocation } from "react-router-dom";

import YouTube from 'react-youtube';

import VideoController from './VideoController';

const VideoComponent = props => {
    const [config, setConfig] = useState({
        autoplay: false,
        controls: true,
        disablekb: true,
        loop: false,
    });
    const { onReady } = props;
    const { search } = useLocation();
    const params = new URLSearchParams(search);
    const videoId = params.get('videoId');
    return <Box>
        <Grid container>
            <Grid item xs="auto">
                <YouTube 
                    videoId={videoId}
                    onReady={onReady}
                    opts={{
                        width: 426,
                        height: 240,
                        playerVars: config
                    }} />
            </Grid>
            <Grid item xs>
                <VideoController config={config} 
                    onControllerChanged={config => setConfig(config) }/>
            </Grid>
        </Grid>
    </Box>;
};

export default VideoComponent;
