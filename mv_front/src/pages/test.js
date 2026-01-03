import React, { useEffect, useState } from 'react';
import AddMediaDialog from '../components/Main/AddMediaDialog';
import { fetchMedia } from '../api/mediaAPI';


const Test = () => {
    const [listOfMedia, setListOfMedia] = useState([]);

    useEffect(() => {
        // Fetching media list from an API
        const fetchMediaList = async () => {
            const media = await fetchMedia();
            setListOfMedia(media);
        };

        fetchMediaList();
    }, []);

    return (
    <>
        <AddMediaDialog 
            open={true} 
            onClose={() => console.log('Close clicked')}
            onSave={() => console.log('Save clicked')}
            listOfMedia={listOfMedia}
        />
    </>
)};

export default Test;
