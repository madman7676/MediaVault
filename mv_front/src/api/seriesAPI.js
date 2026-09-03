import config from '../config.json';
import axios from 'axios';

const API_BASE_URL = `${config.API_BASE_URL}/api/series`;

export const fetchSeries = async (tags = '', filterMode = 'include') => {
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

export const fetchSeriesSeasonsAndEpisodesById = async (serieId) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/${serieId}/episodes`);
        return response.data;
    } catch (error) {
        console.error(`Failed to fetch media by ID: ${error.message}`);
        throw error;
    }
};