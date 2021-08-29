import { Button, TextField, Box } from '@material-ui/core';
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
  const { postAPI } = props;
  const [title, setTitle] = useState('');
  const [url, setURL] = useState('');
  const { user } = window.django;
  const handleSubmit = event => {
    event.preventDefault();
    postAPI({
      'user': user.id,
      'title': title,
      'url': url,
      'data_type': 'video/mp4',
    })
  };

  return (
    <Box m={1}>
      <Helmet>
        <script src="/static/users/js/file-direct-upload.js" />
      </Helmet>
      <form className={classes.root} onSubmit={handleSubmit}>
        <TextField
          style={{ margin: 8 }}
          fullWidth
          id="title"
          label="タイトル"
          required={true}
          value={title}
          onInput={ e=>setTitle(e.target.value)} />
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
          id="id_movie"
          required={true}
          value={url}
          onChange={value => {
            setURL(value);
          }}
          />
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
