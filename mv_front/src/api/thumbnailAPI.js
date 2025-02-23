import axios from 'axios';
import config from '../config.json';
const API_BASE_URL = config.API_BASE_URL + '/api/thumbnail';

export const fetchThumbnail = async (folder_name) => {
    const cacheKey = `thumbnail_${folder_name}`;
    const cachedThumbnail = sessionStorage.getItem(cacheKey);

    if (cachedThumbnail) {
        return cachedThumbnail;
    }

    try {
        const response = await axios.get(`${API_BASE_URL}`, {
            params: { folder_name: folder_name },
        });

        const thumbnailUrl = `${response.config.url}?folder_name=${folder_name}`;
        sessionStorage.setItem(cacheKey, thumbnailUrl);
        return thumbnailUrl;
    } catch (err) {
        console.error(`Failed to fetch thumbnail for ${folder_name}:`, err);
        return null;
    }
};
