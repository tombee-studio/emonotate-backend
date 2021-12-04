import React, { useEffect } from 'react';
import { useState } from 'react';
import SearchItem from './SearchItem';
import { ImageList, ImageListItem } from '@material-ui/core';
import YouTubeDataAPI from '../../helper/YouTubeDataAPI';

const SearchResultList = props => {
    const { keyword } = props;
    const { YOUTUBE_API_KEY } = window.django;
    const [pageToken, setPageToken] = useState(undefined);
    const [loading, setLoading] = useState(false);
    const [items, setItems] = useState([]);
    const api = new YouTubeDataAPI();
    useEffect(() => {
        setLoading(true);
    
        const timeOutId = setTimeout(() => {
            api.get({ 'q': keyword, 'type': 'video', 
            'part': 'snippet', 'key': YOUTUBE_API_KEY, 'maxResults': 12 })
            .then(json => {
                setItems(json.items);
                setPageToken(json.nextPageToken);
            })
            .catch(err => {
                alert(err.status);
            });
        }, 2000);
    
        return () => {
            clearTimeout(timeOutId);
        };
      }, [keyword]);
    return (<ImageList cols={4} gap={16} style={{bgcolor: "#000"}}>
        { items.map(item => <ImageListItem
            key={item.id.videoId} 
            component="a" 
            href={'/app/curves/?videoId=' + item.id.videoId}>
            <SearchItem item={item} key={item.id.videoId} />
        </ImageListItem>) }
    </ImageList>);
};

export default SearchResultList;
