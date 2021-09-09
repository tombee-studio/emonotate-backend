import React, { useState, useEffect } from 'react';
import { Redirect, Route } from 'react-router-dom';
import ObserverComponent from '../components/room-page/ObserverComponent';

import RequestListAPI from '../helper/RequestListAPI';

const RoomPage = props => {
    const { id }  = props;
    const [request, setRequest] = useState(false);
    useEffect(() => {
        const api = new RequestListAPI();
        api.getItem(id, {
            'format': 'json'
        }).then(request => {
            if(request.owner.id != window.django.user.id) 
                throw 'access denied';
            setRequest(request);
        }).catch(message => {
            setRequest({
                redirect: true,
                message: message
            });
        });
    }, []);
    return (
        <Route render={
            props => {
                if(!request) {
                    return <div />
                } else if(!request.redirect) {
                    return <ObserverComponent request={ request } />
                } else {
                    return <Redirect to="/app/request/"/>
                }
            } 
        }/>
    );
}

export default RoomPage; 