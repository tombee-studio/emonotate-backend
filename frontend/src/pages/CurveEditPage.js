import React, { useEffect, useState } from 'react';
import { Route } from 'react-router-dom';
import CurvesListAPI from '../helper/CurvesListAPI';

const CurveEditPage = props => {
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
                if(!curve) return <div>{`${id}を検索しています...`}</div>;
                else if(curve.user.id == window.django.user.id)
                    return <div>{`${id}を編集します...`}</div>;
                else return <div>{`${id}を閲覧します...`}</div>;
            } 
        }/>
    );
}

export default CurveEditPage; 