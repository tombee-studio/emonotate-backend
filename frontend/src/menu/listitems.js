import React from 'react';
import { Badge } from '@mui/material';
import { ListSubheader } from '@mui/material';
import ListItem from '@mui/material/ListItem';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import HomeIcon from '@mui/icons-material/Home';
import HistoryIcon from '@mui/icons-material/History';
import MovieIcon from '@mui/icons-material/Movie';
import TextFormatIcon from '@mui/icons-material/TextFormat';
import MailIcon from '@mui/icons-material/Mail';
import PersonIcon from '@mui/icons-material/Person';

export const mainListItems = (numRequest) => {
  return (
    <div>
      <ListSubheader>一般</ListSubheader>
      <ListItem button component="a" href="/app/dashboard/">
        <ListItemIcon>
          <HomeIcon />
        </ListItemIcon>
        <ListItemText primary="ホーム" />
      </ListItem>
      <ListItem button component="a" href="/app/profile/">
        <ListItemIcon>
          <PersonIcon />
        </ListItemIcon>
        <ListItemText primary="プロファイル" />
      </ListItem>
      <ListItem button component="a" href="/app/history/">
        <ListItemIcon>
          <HistoryIcon />
        </ListItemIcon>
        <ListItemText primary="履歴" />
      </ListItem>
      { window.django.user.permissions.has('users.add_content') &&
        <div>
          <ListItem button component="a" href="/app/content/">
            <ListItemIcon>
              <MovieIcon />
            </ListItemIcon>
            <ListItemText primary="コンテンツ" />
          </ListItem>
          <ListItem button component="a" href="/app/word/">
            <ListItemIcon>
              <TextFormatIcon />
            </ListItemIcon>
            <ListItemText primary="表現語" />
          </ListItem>
        </div>
      }
      <ListSubheader>実験者ツール</ListSubheader>
      <ListItem button component="a" href="/app/requests/">
        <ListItemIcon>
        <Badge badgeContent={numRequest} color="primary">
          <MailIcon />
        </Badge>
        </ListItemIcon>
        <ListItemText primary="実験" />
      </ListItem>
    </div>
  );
};
