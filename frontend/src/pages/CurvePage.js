import { 
    CircularProgress,
    ButtonGroup,
    Box,
    Button,
    Snackbar,
    Grid,
} from '@mui/material';
import React, { useState, useEffect } from 'react';
import { Route, useLocation } from 'react-router-dom';

import CurvesListAPI from "../helper/CurvesListAPI";
import CurveWithYouTubeAPI from "../helper/CurveWithYouTubeAPI";
import CurveComponent from "../components/curve-page/CurveComponent";

const CurvePage = props => {
    // const { search } = useLocation();
    // const params = new URLSearchParams(search);
    // const videoId = params.get('videoId');
    const { id }  = props;
    const [useSnackbar, setSnackbar] = useState(false);
    const [curve, setCurveData] = useState({
        "values": null,
        "version": "0.1.1",
        "room_name": "",
        "locked": false,
        "user": django.user.id,
        "content": {
            "id": 3394,
            "title": "Orangestar - DAYBREAK FRONTLINE (feat. IA) Official Video",
            "url": "https://www.youtube.com/watch?v=emrt46SRyYs",
            "video_id": "emrt46SRyYs",
            "user": 1
        },
        "value_type": {
            "title": "幸福度",
            "axis_type": 1,
            "user": 1
        }
    });
    const create = ev => {
        const api = new CurveWithYouTubeAPI();
        curve["value_type"] = 1
        curve["youtube"] = curve["content"]
        api.create(curve)
            .then(json => {
                handleClick();
            })
            .catch(err => {
                alert(err);
            });
    };
    const update = ev => {};
    const handleClick = () => {
        setSnackbar(true);
    };
    const handleClose = (event, reason) => {
        if (reason === 'clickaway') return;
        setSnackbar(false);
        window.location.href = '/';
    };
    useEffect(() => {
        if(id) {
            const api = new CurvesListAPI();
            api.getItem(id, {
                'format': 'json'
            }).then(curve => {
                setCurveData(curve);
            }).catch(message => {
                alert(message);
            });
        }
    }, []);
    console.log(curve);
    return (
        <Route render={
            props => {
                if(curve.content == null) {
                    return <Box m={2}>
                        <CircularProgress />
                    </Box>
                } else if(id) {
                    return (<Box m={2}>
                        <CurveComponent curve={curve} videoId={curve.content.video_id}
                            onChangeCurve={curve => {
                                console.log(curve);
                                setCurveData(curve);
                            }} />
                        <Grid container spacing={2}>
                            <Grid item>
                                <ButtonGroup>
                                    <Button variant="outlined" onClick={update}>更新</Button>
                                </ButtonGroup>
                            </Grid>
                        </Grid>
                        <Snackbar
                            open={useSnackbar}
                            autoHideDuration={3000}
                            onClose={handleClose}
                            message="更新しました"
                        />
                    </Box>);
                } else {
                    return (<Box m={2}>
                        <CurveComponent curve={curve} videoId={curve.content.video_id}
                            onChangeCurve={curve => setCurveData(curve)} />
                        <ButtonGroup>
                            <Button variant="outlined" onClick={create}>作成</Button>
                        </ButtonGroup>
                        <Snackbar
                            open={useSnackbar}
                            autoHideDuration={3000}
                            onClose={handleClose}
                            message="作成しました"
                        />
                    </Box>);
                }
            } 
        }/>
    );
}

export default CurvePage;