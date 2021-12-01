import React from 'react';

import { Box, Typography } from '@material-ui/core';

const SearchItem = props => {
    const { item, imgSize } = props;
    const { snippet } = item;
    return (<Box m={2}>
        <Typography>{snippet.title}</Typography>
        <Typography>{snippet.channelTitle}</Typography>
    </Box>);
};

export default SearchItem;
