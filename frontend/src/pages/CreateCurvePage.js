import React, { useState } from 'react';
import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import MakeCurveComponent from '../components/create-curve-page/MakeCurveComponent';
import { Box, Select, MenuItem, CircularProgress } from '@mui/material';

import ValueTypeListAPI from '../helper/ValueTypeListAPI';
import ContentsListAPI from '../helper/ContentsListAPI';

const CreateCurvePage = (props) => {
  const search = useLocation().search;
  const query = new URLSearchParams(search);
  if(!query.get('content')) window.location.href = '/';

  const valuetypeListApi = new ValueTypeListAPI();
  const contentsListAPI = new ContentsListAPI();

  const [content, setContent] = useState({});
  const [valuetypes, setValueTypes] = useState([]);
  const [curveType, setCurveType] = useState(0);
  const content_id = query.get('content');
  const value_type_id = query.get('value_type');
  const room_name = query.get('room') || `content=${content_id} value_type_id=${value_type_id}`;
  const counts = query.get('counts') || 1;

  useEffect(() => {
    const apis = [];
    apis.push(new Promise(resolve => {
      valuetypeListApi.get(_valuetypes => {
        resolve(_valuetypes.models);
      });
    }));
    if(value_type_id) {
      apis.push(new Promise(resolve => {
        valuetypeListApi.getItem(value_type_id)
        .then(data => {
          resolve(data);
        });
      }));
    }
    if(content_id) {
      apis.push(new Promise(resolve => {
        contentsListAPI.getItem(content_id)
        .then(data => {
          resolve(data);
        });
      }));
    }
    Promise.all(apis)
      .then(data => {
        if(data.length <= 2) {
          const [_valuetypes, _content] = data;
          setValueTypes(_valuetypes);
          setContent(_content);
        } else if(data.length > 2) {
          const [_valuetypes, _valuetype, content] = data;
          setValueTypes(_valuetypes);
          setCurveType(_valuetype);
          setContent(content);
        }
      });
  }, []);

  return (
    <Box m={2}>
      {
        valuetypes.length > 0 ?
          <Select
          labelId="curvetype-select"
          id="curvetype-select"
          defaultValue = {curveType.id || "選択してください"}
          value={curveType.id || ""}
          onChange={event => {
            window.location.href =
              `/app/new/curve?content=${query.get('content')}&value_type=${event.target.value}`;
          }}
        >
          {
            valuetypes.map(element => (
              <MenuItem 
                key={element.id}
                value={element.id}>
                  {element.title}
              </MenuItem>
            ))
          }
        </Select>
        : <CircularProgress />
      }
      { 
      content.url && curveType &&
        <MakeCurveComponent 
          content={content} 
          valueType={curveType} 
          roomName={room_name}
          counts={Number(counts)} />
      }
    </Box>
  );
};

export default CreateCurvePage;
