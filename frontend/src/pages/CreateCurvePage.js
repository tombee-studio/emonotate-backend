import React, { useState } from 'react';
import { useEffect } from 'react';
import MakeCurveComponent from '../components/CreateCurvePage/MakeCurveComponent';
import { Box, Select, MenuItem } from '@material-ui/core';

import ValueTypeListAPI from '../helper/ValueTypeListAPI';

const CreateCurvePage = (props) => {
  const { params } = props.match;
  const id = parseInt(params.id, 10);
  const api = new ValueTypeListAPI();
  const [content, setContent] = useState({
    "id": 1,
    "user": {
        "id": 1,
        "username": "",
        "email": "",
        "last_login": "",
        "is_active": true,
        "date_joined": "",
        "last_updated": ""
    },
    "title": "",
    "url": ""
  });
  const [valuetypes, setValueTypes] = useState([]);
  const [curveType, setCurveType] = useState(0);
  useEffect(() => {
    fetch(`/api/contents/${id}?format=json`)
      .then(res => res.json())
      .then(content => {
        setContent(content);
      });
    api.get(_valuetypes => {
      setValueTypes(_valuetypes.models);
    });
  }, []);

  return (
    <Box m={2}>
      <Select
        labelId="curvetype-select"
        id="curvetype-select"
        defaultValue = ""
        value={curveType}
        onChange={event => {
          setCurveType(event.target.value)
        }}
        autoWidth
      >
        {
          valuetypes.map(element => (
            <MenuItem key={element.id} value={element}>{element.title}</MenuItem>
          ))
        }
      </Select>
      { 
      content.url && curveType ?
        <MakeCurveComponent content={content} valueType={curveType} /> :
        <div>少々お待ちください</div>
      }
    </Box>
  );
};

export default CreateCurvePage;
