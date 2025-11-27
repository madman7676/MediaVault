import config from '../config.json';
import axios from 'axios';

const API_BASE_URL = `${config.API_BASE_URL}/api/bookmarks`;

export const fetchDefaultBookmarks = async (episode_id) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/skipranges/episode/${episode_id}/default`);
        return response.data;
    } catch (error) {
        console.error(`Failed to fetch all media: ${error.message}`);
        throw error;
    }
};