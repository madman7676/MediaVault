import config from '../config.json';
import axios from 'axios';

const API_BASE_URL = `${config.API_BASE_URL}/api/media`;

export const fetchMedia = async (tags = '', filterMode = 'include') => {
    try {
        const response = await axios.get(`${API_BASE_URL}/`, {
            params: {
                tags,
                filter_mode: filterMode
            }
        });
        return response.data;
    } catch (error) {
        console.error(`Failed to fetch all media: ${error.message}`);
        throw error;
    }
};

export const fetchMediaById = async (mediaId) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/${mediaId}`);
        return response.data;
    } catch (error) {
        console.error(`Failed to fetch media with ID ${mediaId}: ${error.message}`);
        throw error;
    }
};

export const fetchMediaStructurePerview = async (path) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/media_structure_perview`, {
            path: path
        });
        return response.data;
    } catch (error) {
        console.error(`Failed to fetch select folder: ${error.message}`);
        throw error;
    }
};