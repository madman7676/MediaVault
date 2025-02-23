import config from '../config.json';
import axios from 'axios';

const API_BASE_URL = `${config.API_BASE_URL}/api/metadata`;

export const addTagToItems = async (ids, tag) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/add_tag`, { ids, tag });
        return response.data.message;
    } catch (error) {
        console.error(`Failed to add tag to items: ${error.message}`);
        throw error;
    }
};

export const fetchTimeToSkip = async (path, name) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/time_to_skip`, {
            params: { path, name }, // Передача параметрів у GET-запит
            headers: { 'Content-Type': 'application/json' }, // Опціональний заголовок
        });
        return response.data.timeToSkip || [];
    } catch (error) {
        console.error(`Failed to fetch timeToSkip: ${error.message}`);
        throw error;
    }
};

export const updateTimeToSkip = async (path, name, timeToSkip) => {
    try {
        await axios.post(`${API_BASE_URL}/time_to_skip`, { path, name, timeToSkip });
        return true;
    } catch (error) {
        console.error(`Failed to update timeToSkip: ${error.message}`);
        throw error;
    }
};

export const bulkUpdateTimeToSkip = async (path, name, timeToSkip) => {
    try {
        await axios.post(`${API_BASE_URL}/time_to_skip/bulk`, { path, name, timeToSkip });
        return true;
    } catch (error) {
        console.error(`Failed to update timeToSkip: ${error.message}`);
        throw error;
    }
};

export const fetchMetadataById = async (itemId) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/item/${itemId}`);
        return response.data.item;
    } catch (error) {
        console.error(`Failed to fetch metadata by ID: ${error.message}`);
        throw error;
    }
};

export const fetchMetadataItem = async (path) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/item`, { params: { path } });
        return response.data.item;
    } catch (error) {
        console.error(`Failed to fetch metadata item: ${error.message}`);
        throw error;
    }
};

export const searchMetadata = async (query) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/search`, { params: { query } });
        return response.data.results;
    } catch (error) {
        console.error(`Failed to search metadata: ${error.message}`);
        throw error;
    }
};

export const updateMetadataById = async (itemId, updates) => {
    try {
        const response = await axios.put(`${API_BASE_URL}/item/${itemId}`, updates);
        return response.data.item;
    } catch (error) {
        console.error(`Failed to update metadata by ID: ${error.message}`);
        throw error;
    }
};

export const forceUpdateMetadata = async () => {
    try {
        const response = await axios.post(`${API_BASE_URL}/force-update`);
        return response.data.message;
    } catch (error) {
        console.error(`Failed to force update metadata: ${error.message}`);
        throw error;
    }
};

export const deleteMetadata = async (path) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/delete`, { path });
        return response.data.message;
    } catch (error) {
        console.error(`Failed to delete metadata: ${error.message}`);
        throw error;
    }
};

export const addOrUpdateMetadata = async (metadata) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/add`, metadata);
        return response.data.message;
    } catch (error) {
        console.error(`Failed to add or update metadata: ${error.message}`);
        throw error;
    }
};

export const fetchMetadata = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}`);
        return response.data;
    } catch (error) {
        console.error(`Failed to fetch metadata: ${error.message}`);
        throw error;
    }
};
