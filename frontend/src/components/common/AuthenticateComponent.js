import React from 'react';

import IconButton from '@mui/material/IconButton';
import MeetingRoomIcon from '@mui/icons-material/MeetingRoom';
import ExitToAppIcon from '@mui/icons-material/ExitToApp';

import AuthenticateAPI from '../../helper/AuthenticateAPI';

const AuthenticateComponent = props => {
    if(django.user.group == "Guest")
      return (
        <IconButton
          edge="end"
          aria-label="account of current user"
          aria-haspopup="true"
          color="inherit"
          component="a"
          href="/app/login/"
          size="large">
          <MeetingRoomIcon />
        </IconButton>
      );
    else
      return (
        <IconButton
          edge="end"
          aria-label="account of current user"
          aria-haspopup="true"
          color="inherit"
          size="large"
          onClick={_ => {
            const api = new AuthenticateAPI();
            api.logout().then(_ => {
              window.location = '/';
            });
          }}>
          <ExitToAppIcon />
        </IconButton>
      );
};

export default AuthenticateComponent;
