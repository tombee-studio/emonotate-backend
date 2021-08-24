import { Button, TextField, Box } from '@material-ui/core';
import { Select, MenuItem, FormControl } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import React from 'react';
import { useState } from 'react';

const useStyles = makeStyles((theme) => ({
  root: {
    display: 'flex',
    flexWrap: 'wrap',
  },
  textField: {
    marginLeft: theme.spacing(1),
    marginRight: theme.spacing(1),
    width: '25ch',
  },
  inputFileBtnHide: {
    opacity:0,
    appearance: "none",
    position: "absolute",
  }
}));

const AddContent = (props) => {
  const classes = useStyles();
  const { postAPI } = props;
  const [title, setTitle] = useState('');
  const [axisType, setAxisType] = useState(0);
  const handleSubmit = event => {
    event.preventDefault();
    postAPI({
      'title': title,
      'axis_type': axisType,
    })
  };

  return (
    <Box m={1}>
      <form className={classes.root} onSubmit={handleSubmit}>
        <TextField
          style={{ margin: 8 }}
          fullWidth
          id="title"
          label="タイトル"
          required={true}
          value={title}
          onInput={ e=>setTitle(e.target.value)} />
        <FormControl>
          <Select
            labelId="valuetype-select"
            id="valuetype-select"
            defaultValue = ""
            value={axisType}
            onChange={event => {
              setAxisType(event.target.value);
            }}
            autoWidth
          >
            <MenuItem value={1}>対義語対を持つ</MenuItem>
            <MenuItem value={2}>対義語対を持たない</MenuItem>
          </Select>
        </FormControl>
        <Button
          id="button"
          type="submit"
          color="primary"
          variant="contained">
            送信
        </Button>
      </form>
    </Box>
  );
};

export default AddContent;
