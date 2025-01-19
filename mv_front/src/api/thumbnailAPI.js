import axios from 'axios';
import config from '../config.json';
const API_BASE_URL = config.API_BASE_URL + '/api/thumbnail';

export const fetchThumbnail = async (videoPath) => {
    const cacheKey = `thumbnail_${videoPath}`;
    const cachedThumbnail = sessionStorage.getItem(cacheKey);

    if (cachedThumbnail) {
        return cachedThumbnail;
    }

    try {
        const response = await axios.get(`${API_BASE_URL}`, {
            params: { video_path: videoPath },
        });

        const thumbnailUrl = `${response.config.url}?video_path=${videoPath}`;
        sessionStorage.setItem(cacheKey, thumbnailUrl);
        return thumbnailUrl;
    } catch (err) {
        console.error(`Failed to fetch thumbnail for ${videoPath}:`, err);
        return null;
    }
};
