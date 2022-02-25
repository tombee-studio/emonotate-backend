import React from "react";
import { 
    Box,
    Grid,
} from "@mui/material";
import { useState } from "react";
import YouTube from 'react-youtube';

import VideoController from './VideoController';

const VideoComponent = props => {
    const { value_type } = props;
    const [config, setConfig] = useState({
        autoplay: false,
        controls: true,
        disablekb: true,
        loop: false,
    });
    const { onReady, videoId } = props;
    return <Box m={2}>
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
                <VideoController config={config} value_type={value_type}
                    onControllerChanged={config => setConfig(config) }/>
            </Grid>
        </Grid>
    </Box>;
};

export default VideoComponent;
