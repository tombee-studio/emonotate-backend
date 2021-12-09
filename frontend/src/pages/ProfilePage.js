import React from 'react';
import Box from '@mui/material/Box';
import ProfileComponent from '../components/profile-page/ProfileComponent';

const ProfilePage = (props) => {
    return (
        <Box m={2}>
            <Box m={1}>
                <ProfileComponent user={window.django.user} />
            </Box>
        </Box>
    );
}

export default ProfilePage;
