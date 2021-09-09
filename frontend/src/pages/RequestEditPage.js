import React, { useEffect, useState } from 'react';
import { Redirect, Route } from 'react-router-dom';
import RequestListAPI from '../helper/RequestListAPI';
import RequestComponent from '../components/request-edit-page/RequestComponent';

const RequestEditPage = props => {
    const { id } = props;
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
                    return <RequestComponent request={ request } />
                } else {
                    return <Redirect to="/app/request/"/>
                }
            } 
        }/>
    );
}

export default RequestEditPage; 