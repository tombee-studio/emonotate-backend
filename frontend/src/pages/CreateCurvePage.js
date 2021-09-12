import React, { useState } from 'react';
import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import MakeCurveComponent from '../components/create-curve-page/MakeCurveComponent';
import { Box, Select, MenuItem } from '@material-ui/core';

import ValueTypeListAPI from '../helper/ValueTypeListAPI';

const CreateCurvePage = (props) => {
  const search = useLocation().search;
  const query = new URLSearchParams(search);
  if(!query.get('content')) window.location.href = '/';

  const api = new ValueTypeListAPI();
  const [content, setContent] = useState({});
  const [valuetypes, setValueTypes] = useState([]);
  const [curveType, setCurveType] = useState(0);
  
  if(!query.get('value_type')) {
      useEffect(() => {
          api.get(_valuetypes => {
              setValueTypes(_valuetypes.models);
          });
      }, []);
      return (
          <Box m={2}>
              <Select
                  labelId="curvetype-select"
                  id="curvetype-select"
                  defaultValue = {""}
                  value={curveType}
                  onChange={event => {
                      window.location.href = 
                        `/app/new/curve?content=${query.get('content')}&value_type=${event.target.value.id}`;
                  }}
                  autoWidth
              >
              {
                  valuetypes.map(element => (
                      <MenuItem key={element.id} value={element}>{element.title}</MenuItem>
                  ))
              }
            </Select>
          </Box>);
  }

  const content_id = query.get('content');
  const value_type_id = query.get('value_type');

  useEffect(() => {
    fetch(`/api/contents/${content_id}?format=json`)
      .then(res => res.json())
      .then(content => {
          setContent(content);
        });
      api.get(_valuetypes => {
          setValueTypes(_valuetypes.models);
        });
      api.getItem(value_type_id)
        .then(data => {
          setCurveType(data);
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
          window.location.href = 
            `/app/new/curve?content=${query.get('content')}&value_type=${event.target.value.id}`;
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
