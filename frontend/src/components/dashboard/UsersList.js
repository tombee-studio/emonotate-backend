import React from 'react';
import { Pagination } from '@material-ui/lab';
import { Card } from '@material-ui/core';

class UsersList extends React.Component {
  constructor(props) {
    super(props);

    this.state = {};
  }

  componentDidMount() {
    fetch('/api/users/?format=json')
      .then(res => res.json())
      .then(users => {
        this.setState({
          users: users
        });
      }); 
  }

  render() {
    const { users } = this.state;
    const handlePaginate = (e, page) => {
      fetch(`/api/users/?format=json&page=${page}`)
        .then(res => {
          return res.json();
        })
        .then(users => {
          this.setState({
            users: users
          });
        });
    };
    if(users) {
      return (
        <Card>
          <Pagination 
            count={users.pagination.total_pages} 
            variant="outlined" 
            shape="rounded"
            onChange={handlePaginate} />
        </Card>
      );
    } else {
      return (<Card />);
    }
  };
};

export default UsersList;
