import React, { useState } from 'react';
import { useEffect } from 'react';
import MakeCurveComponent from '../components/CreateCurvePage/MakeCurveComponent';
import { Box } from '@material-ui/core';

const CreateCurvePage = (props) => {
  const { params } = props.match;
  const id = parseInt(params.id, 10);
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
  useEffect(() => {
    fetch(`/api/contents/${id}?format=json`)
      .then(res => res.json())
      .then(content => {
        setContent(content);
      });
  }, []);

  return (
    <Box m={2}>
      { 
      content.url ?
        <MakeCurveComponent content={content} valueType={{
          "id": 1,
          "title": "幸福度",
          "axis_type": 1
        }} /> :
        <div>少々お待ちください</div>
      }
    </Box>
  );
};

export default CreateCurvePage;
