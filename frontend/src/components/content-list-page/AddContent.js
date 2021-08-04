import { Button, FormControl, TextField, Box } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import React from 'react';
import { useState } from 'react';
import { Helmet } from 'react-helmet';

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
  const [data, setData] = useState({});

  return (
    <Box m={1}>
      <Helmet>
        <script src="/static/users/js/file-direct-upload.js" />
      </Helmet>
      <FormControl className={classes.root}>
        <TextField
          style={{ margin: 8 }}
          placeholder="タイトル"
          fullWidth
          id="filled-basic"
          label="タイトル"
          onChange={(ev) => {
            setData({
              'title': ev.currentTarget.value,
            })
          }} />
        <Button
          component="label"
        >
          ファイルを選択
          <input
            type="file"
            id="id_file"
            className={classes.inputFileBtnHide}
          />
        </Button>
        <TextField
          style={{ margin: 8 }}
          placeholder="URL"
          fullWidth
          id="id_movie"
          label="URL"
          onChange={(ev) => {
            setData({
              'url': ev.currentTarget.value,
            })
          }} />
        <Button
          disabled={!(data.url && data.title)}
          color="primary"
          variant="contained">
            コンテンツの追加
        </Button>
      </FormControl>
    </Box>
  );
};

export default AddContent;
