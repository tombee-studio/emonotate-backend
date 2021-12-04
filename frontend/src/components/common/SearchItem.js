import React from 'react';

import { 
    Box, ImageListItemBar
} from '@material-ui/core';

const SearchItem = props => {
    const { item, imgSize } = props;
    const { snippet } = item;
    return (
        <Box>
            <img
                srcSet={snippet.thumbnails["medium"].url}
                alt={item.title}
                loading="lazy"
            />
            <ImageListItemBar
                title={snippet.title}
                subtitle={snippet.channelTitle}
            />
        </Box>);
};

export default SearchItem;
