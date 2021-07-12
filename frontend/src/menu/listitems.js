import React from 'react';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import EditIcon from '@material-ui/icons/Edit';
import DashboardIcon from '@material-ui/icons/Dashboard';
export const mainListItems = (
  <div>
    <ListItem button component="a" href="/app/dashboard/">
      <ListItemIcon>
        <DashboardIcon />
      </ListItemIcon>
      <ListItemText primary="ダッシュボード" />
    </ListItem>
    <ListItem button component="a" href="/app/edit/">
      <ListItemIcon>
        <EditIcon />
      </ListItemIcon>
      <ListItemText primary="編集" />
    </ListItem>
  </div>
);
