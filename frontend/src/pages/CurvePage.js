import { 
    CircularProgress,
    ButtonGroup,
    Box,
    Button,
    Snackbar,
    Grid,
} from '@mui/material';
import React, { useState, useEffect } from 'react';
import { Route } from 'react-router-dom';

import CurvesListAPI from "../helper/CurvesListAPI";
import CurveComponent from "../components/curve-page/CurveComponent";

const CurvePage = props => {
    const { id, params }  = props;
    const [loading, setLoading] = useState(false);
    const [useSnackbar, setSnackbar] = useState(false);
    const [curve, setCurveData] = useState({});
    const create = ev => {
        const api = new CurvesListAPI();
        api.create(request)
            .then(json => {
                handleClick();
            })
            .catch(err => {
                alert(err);
            });
    };
    const update = ev => {
        const api = new CurvesListAPI();
        api.update(request.id, request)
            .then(json => {
                handleClick();
            })
            .catch(err => {
                alert(err);
            });
    };
    const handleClick = () => {
        setSnackbar(true);
    };
    const handleClose = (event, reason) => {
        if (reason === 'clickaway') return;
        setSnackbar(false);
    };
    useEffect(() => {
        if(id) {
            const api = new CurvesListAPI();
            api.getItem(id, {
                'format': 'json'
            }).then(curve => {
                setLoading(true);
                setCurveData(curve);
            }).catch(message => {
                alert(message);
            });
        } else {
            setLoading(true);
        }
    }, []);
    return (
        <Route render={
            props => {
                if(!loading) {
                    return <Box m={2}>
                        <CircularProgress />
                    </Box>
                } else if(id) {
                    return (<Box m={2}>
                        <CurveComponent curve={curve} 
                            onChangedCurve={curve => setCurveData(curve)} />
                        <Grid container spacing={2}>
                            <Grid item>
                                <ButtonGroup>
                                    <Button variant="outlined" onClick={update}>更新</Button>
                                </ButtonGroup>
                            </Grid>
                            <Grid item>
                                <ButtonGroup>
                                    <Button variant="outlined" onClick={download}>ダウンロード</Button>
                                    <Button variant="outlined" onClick={sendMails}>メール送信</Button>
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
                        <CurveComponent curve={curve} 
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