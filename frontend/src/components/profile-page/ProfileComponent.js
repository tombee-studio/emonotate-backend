import React from 'react';

export default class ProfileComponent extends React.Component {
    render() {
        const { user } = this.props;
        console.log(user);
        return (<div />);
    }
};
