import { useEffect } from "react";

const FILTER_STORAGE_KEY = 'mediaVaultFilter';
const TAGS_STORAGE_KEY = 'mediaVaultTags';

const useLocalStorage = (initialState) => {
    // 1. Функції для отримання початкових значень (статичні)
    const getInitialFilter = () => {
        try {
            return localStorage.getItem(FILTER_STORAGE_KEY) || initialState.filter;
        } catch {
            return initialState.filter;
        }
    };

    const getInitialTags = () => {
        try {
            const tags = localStorage.getItem(TAGS_STORAGE_KEY);
            return tags ? JSON.parse(tags) : initialState.selectedTags;
        } catch {
            return initialState.selectedTags;
        }
    };

    // 2. Функції для збереження (приймають значення як параметри)
    const saveToLocalStorage = (filter, selectedTags) => {
        // Зберігаємо фільтр
        try {
            localStorage.setItem(FILTER_STORAGE_KEY, filter);
        } catch (error) {
            console.error('Failed to save filter to localStorage:', error);
        }

        // Зберігаємо теги
        try {
            localStorage.setItem(TAGS_STORAGE_KEY, JSON.stringify(selectedTags));
        } catch (error) {
            console.error('Failed to save tags to localStorage:', error);
        }
    };

    return {
        getInitialFilter,
        getInitialTags,
        saveToLocalStorage
    };
};

export default useLocalStorage;