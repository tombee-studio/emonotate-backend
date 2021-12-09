import React, { useEffect, useState } from 'react';
import { Route } from 'react-router-dom';
import { CircularProgress, Box } from '@mui/material';
import CurvesListAPI from '../helper/CurvesListAPI';
import EditCurveComponent from '../components/edit-curve-page/EditCurveComponent';

const EditCurvePage = props => {
    const { id } = props;
    const [ curve, setCurve ] = useState(false);
    useEffect(() => {
    const api = new CurvesListAPI();
        api.getItem(id)
            .then(curve => {
                setCurve(curve);
            });
    }, []);
    return (
        <Route render={
            props => {
                if(!curve) return (<Box m={2}>
                    <CircularProgress />
                </Box>);
                else if(curve.user.id == window.django.user.id)
                    return <EditCurveComponent 
                        content={curve.content}
                        valueType={curve.value_type}
                        values={curve.values}
                    />;
                else return <div>{`${id}を閲覧します...`}</div>;
            } 
        }/>
    );
}

export default EditCurvePage; 