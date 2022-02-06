import React, { useEffect } from "react";

import { Box, Grid } from "@mui/material";
import VideoComponent from "./VideoComponent";
import EmotionalArcField from "../../helper/EmotionalArcField";

const CurveComponent = props => {
    CurveComponent.inputField = undefined;
    var isLoadedScript = false;
    var player = undefined;
    const { curve, onChangeCurve, videoId } = props;
    const createEmotionalArcField = (player, isLoadedScript) => {
        if(player == undefined || isLoadedScript) return;
        console.log(curve);
        CurveComponent.inputField = new EmotionalArcField("chart", player, {
            maxValue: 1,
            minValue: -1,
            centralValue: 0,
        }, { 
            'r': 12,
            'color': 'black',
        });
        CurveComponent.inputField.OnInit();
        const data = curve.values;
        CurveComponent.inputField.load(data);

        setInterval(() => {
            CurveComponent.inputField.updateVideo();
        }, 100);
    };
    useEffect(() => {
        EmotionalArcField.loadScript("/static/users/d3/d3.min.js")
            .then(() => {
                isLoadedScript = true;
                createEmotionalArcField(player, isLoadedScript);
            });
    }, []);

    return (<Box>
        <Grid container spacing={2}>
            <VideoComponent 
                videoId={videoId}
                onReady={event => {
                player = event.target;
                const videoData = player.getVideoData();
                const curveClone = curve;
                curveClone.content = {
                    'title': videoData.title,
                    'video_id': videoData.video_id,
                    'url': player.getVideoUrl(),
                    'user': django.user.id
                }
                curveClone.values = [{
                    id: 0,
                    x: 0,
                    y: 0,
                    axis: 'v',
                    type: 'fixed',
                    text:   "",
                    reason: "",
                }, {
                    id: 1,
                    x: player.getDuration(),
                    y: 0,
                    axis: 'v',
                    type: 'fixed',
                    text:   "",
                    reason: "",
                }];
                curveClone.room_name = `${videoData.video_id}-${1}`;
                onChangeCurve(curveClone);
                createEmotionalArcField(player, isLoadedScript);
            }} />
            <Grid item xs={12}>
                <svg id="chart" width="100%" height={280} />
            </Grid>
        </Grid>
    </Box>);
};

export default CurveComponent;
