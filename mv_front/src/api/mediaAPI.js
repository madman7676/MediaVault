import config from '../config.json';
import axios from 'axios';

const API_BASE_URL = `${config.API_BASE_URL}/api/media`;

export const fetchAllMedia = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/all`);
        // Повертаємо повне тіло відповіді — бекенд віддає { data: [...] , status_code: ... }
        return response.data;
    } catch (error) {
        console.error(`Failed to fetch all media: ${error.message}`);
        throw error;
    }
};