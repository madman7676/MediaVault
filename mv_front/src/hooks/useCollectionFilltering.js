import { useMemo, useEffect } from 'react';
import { ACTIONS } from '../constants/mediaConstants';

export const useCollectionFiltering = (collections, filter, selectedTags, filterMode, dispatch) => {
  // Фільтрація колекцій з використанням useMemo
  const filteredResults = useMemo(() => {
    let filtered = collections;

    // Фільтрація по типу
    if (filter !== 'all') {
      if (filter === 'series_combined') {
        filtered = filtered.filter(collection => 
          collection.type === 'series' || collection.type === 'online_series');
      } else {
        filtered = filtered.filter(collection => collection.type === filter);
      }
    }

    // Фільтрація по тегам
    if (selectedTags.includes('∅')) {
      // Показуємо тільки елементи без тегів
      filtered = filtered.filter(collection => !collection.tags || collection.tags.length === 0);
    } else if (selectedTags && selectedTags.length > 0) {
      if (filterMode === 'include') {
        // Включаємо елементи з обраними тегами
        filtered = filtered.filter(collection => 
          collection.tags && selectedTags.some(tag => collection.tags.includes(tag)));
      } else {
        // Виключаємо елементи з обраними тегами
        filtered = filtered.filter(collection => 
          !collection.tags || !selectedTags.some(tag => collection.tags.includes(tag)));
      }
    }

    console.log('Filtered results:', filtered);
    return filtered;
  }, [collections, filter, selectedTags, filterMode]);

  // Оновлюємо відфільтровані колекції коли результат змінюється
  useEffect(() => {
    dispatch({ type: ACTIONS.SET_FILTERED_COLLECTIONS, payload: filteredResults });
  }, [filteredResults, dispatch]);
};