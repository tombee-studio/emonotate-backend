import React from 'react';

import IconButton from '@material-ui/core/IconButton';
import MeetingRoomIcon from '@material-ui/icons/MeetingRoom';
import ExitToAppIcon from '@material-ui/icons/ExitToApp';

const AuthenticateComponent = props => {
    if(django.user.group == "Guest")
      return (<IconButton
        edge="end"
        aria-label="account of current user"
        aria-haspopup="true"
        color="inherit"
        component="a" 
        href="/app/login/"
      >
        <MeetingRoomIcon />
      </IconButton>);
    else
      return (<IconButton
        edge="end"
        aria-label="account of current user"
        aria-haspopup="true"
        color="inherit"
        component="a" 
        href="/app/logout/"
      >
        <ExitToAppIcon />
      </IconButton>);
};

export default AuthenticateComponent;
