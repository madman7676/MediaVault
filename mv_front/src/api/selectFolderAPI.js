import config from '../config.json';
import axios from 'axios';

const API_BASE_URL = `${config.API_BASE_URL}/api/select_folder`;

export const fetchSelectFolder = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/`);
        return response.data;
    } catch (error) {
        console.error(`Failed to fetch select folder: ${error.message}`);
        throw error;
    }
};