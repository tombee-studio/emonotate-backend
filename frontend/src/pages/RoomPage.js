import { 
    CircularProgress,
    ButtonGroup,
    Box,
    Button,
    Snackbar
} from '@material-ui/core';
import React, { useState, useEffect } from 'react';
import { Redirect, Route } from 'react-router-dom';
import ObserverComponent from '../components/room-page/ObserverComponent';

import CurvesListAPI from "../helper/CurvesListAPI";
import RequestListAPI from "../helper/RequestListAPI"

const RoomPage = props => {
    const { id }  = props;
    const [loading, setLoading] = useState(false);
    const [request, setRequest] = useState({
        owner: window.django.user.id
    });
    const [useSnackbar, setSnackbar] = useState(false);
    const create = ev => {
        const api = new RequestListAPI();
        api.create(request)
            .then(json => {
                handleClick();
            })
            .catch(err => {
                alert(err);
            });
    };
    const update = ev => {
        const api = new RequestListAPI();
        request.content = request.content.id;
        request.owner = request.owner.id;
        request.value_type = request.value_type.id;
        api.update(request.id, request)
            .then(json => {
                handleClick();
            })
            .catch(err => {
                alert(err);
            });
    };
    const onClickDownloadButton = (ev) => {
        const api = new CurvesListAPI();
        api.list({
            'format': 'json',
            'search': this.request.room_name,
            'page_size': 200,
        })
        .then(json => {
            this.download(json);
            alert("ダウンロードを終了しました");
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
            const api = new RequestListAPI();
            api.getItem(id, {
                'format': 'json'
            }).then(request => {
                if(request.owner.id != window.django.user.id) 
                    throw 'access denied';
                request.content = request.content.id;
                request.owner = request.owner.id;
                request.value_type = request.value_type.id;
                setRequest(request);
                setLoading(true);
            }).catch(message => {
                setRequest({
                    redirect: true,
                    message: message
                });
            });
        } else {
            setLoading(true);
        }
    }, []);
    return (
        <Route render={
            props => {
                if(!loading) {
                    return <CircularProgress />
                } else if(id) {
                    return (<Box m={2}>
                        <ObserverComponent 
                            request={ request } 
                            onChange={ req => {
                                console.log(req);
                                setRequest(req);
                            } } />
                        <ButtonGroup>
                            <Button variant="outlined" onClick={update}>更新</Button>
                            <Button variant="outlined" onClick={onClickDownloadButton}>ダウンロード</Button>
                        </ButtonGroup>
                        <Snackbar
                            open={useSnackbar}
                            autoHideDuration={3000}
                            onClose={handleClose}
                            message="更新しました"
                        />
                    </Box>);
                } else {
                    return (<Box m={2}>
                        <ObserverComponent 
                            request={ request } 
                            onChange={ request => {
                                setRequest(request);
                            } } />
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

export default RoomPage; 