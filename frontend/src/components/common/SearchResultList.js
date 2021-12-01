import React, { useEffect } from 'react';
import { useState } from 'react';
import SearchItem from './SearchItem';
import { List } from '@material-ui/core';
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
            'part': 'snippet', 'key': YOUTUBE_API_KEY, 'maxResults': 10 })
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
    return (<List m={2}>
        {items.map(item => <SearchItem item={item} 
            key={item.id.videoId}
            imgSize="medium" />)}
    </List>);
};

export default SearchResultList;
