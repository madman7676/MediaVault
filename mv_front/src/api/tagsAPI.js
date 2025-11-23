import config from '../config.json';
import axios from 'axios';

const API_BASE_URL = `${config.API_BASE_URL}/api/tags`;

export const fetchAllTags = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/`);
        return response.data.tags;
    } catch (error) {
        console.error(`Failed to fetch all tags: ${error.message}`);
        throw error;
    }
};

export const addTagToItems = async (ids, tag) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/`, { ids, tag });
        return response.data.message;
    } catch (error) {
        console.error(`Failed to add tag to items: ${error.message}`);
        throw error;
    }
};