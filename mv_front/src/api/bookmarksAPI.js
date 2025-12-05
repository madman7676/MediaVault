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

export const processBulkUpdateforBookmarksChangeLog = async (episode_id, bookmarksChangeLog) => {
    try {
        // await axios.post(`${API_BASE_URL}/time_to_skip`, { episode_id, bookmarks });
        console.log('Updating bookmarks for episode:', episode_id, bookmarksChangeLog);
        return true;
    } catch (error) {
        console.error(`Failed to update timeToSkip: ${error.message}`);
        throw error;
    }
};

// export const processBookmarksChangeLog = async (episode_id, bookmarksChangeLog) => {
//     console.log('API: Processing bookmarks change log for episode:', episode_id, bookmarksChangeLog);
//     return 'not implemented yet';
// }

export const processBookmarksChangeLog = async (episode_id, bookmarksChangeLog) => {
    const handlers = {
        CREATE: processCreateBookmark,
        UPDATE: processUpdateBookmark,
        DELETE: processDeleteBookmark,
    };
    try {
        const changeEntries = Object.entries(bookmarksChangeLog);
        let results = [];
        for (const [id, bookmarks] of changeEntries) {
            const handler = handlers[bookmarks.action];
            if (handler) {
                const result = await handler(id.startsWith("Temp") ? episode_id : id, bookmarks);
                results.push({ id, status: 'success', action: bookmarks.action, result });
            } else {
                results.push({ id, status: 'failed', action: bookmarks.action, error: 'Unknown action' });
            }
        }
        console.log('Updating bookmarks for episode:', episode_id, bookmarksChangeLog);
        return results;
    } catch (error) {
        console.error(`Failed to update timeToSkip: ${error.message}`);
        throw error;
    }
};


const processCreateBookmark = async (episode_id, bookmark) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/episode/${episode_id}/default_skiprange`, { 
            start: bookmark.start, 
            end: bookmark.end, 
            label: bookmark?.label 
        });
        return response.data;
    } catch (error) {
        console.error(`Failed to create bookmarks: ${error.message}`);
        throw error;
    }
};

const processUpdateBookmark = async (bookmark_id, bookmark) => {
    try {
        const response = await axios.put(`${API_BASE_URL}/skiprange/${bookmark_id}`, {
            start: bookmark.start,
            end: bookmark.end,
            label: bookmark?.label
        });
        return response.data;
    } catch (error) {
        console.error(`Failed to update bookmark: ${error.message}`);
        throw error;
    }
};

const processDeleteBookmark = async (bookmark_id) => {
    try {
        await axios.delete(`${API_BASE_URL}/skiprange/${bookmark_id}`);
        return true;
    } catch (error) {
        console.error(`Failed to delete bookmark: ${error.message}`);
        throw error;
    }
};