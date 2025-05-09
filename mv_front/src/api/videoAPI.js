import config from '../config.json';
import axios from 'axios';

const API_BASE_URL = `${config.API_BASE_URL}/api/video`;

export const getAudioTracks = async (path) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/audio-tracks`, {
            params: { path },
            headers: { 'Content-Type': 'application/json' },
        });
        return response.data.tracks || [];
    } catch (error) {
        console.error(`Failed to fetch audio tracks: ${error.message}`);
        throw error;
    }
};