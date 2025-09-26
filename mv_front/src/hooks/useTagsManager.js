import { useState, useEffect, useMemo, useCallback } from "react";

import { ACTIONS } from '../constants/mediaConstants';
import { addTagToItems, fetchAllTags } from '../api/metadataAPI';

// Custom hook для тегів
function useTagsManager(dispatch, selectedTags, collections) {
  const [tags, setTags] = useState([]);

  useEffect(() => {
    const loadTags = async () => {
      try {
        const fetchedTags = await fetchAllTags();
        setTags(fetchedTags);
      } catch (error) {
        console.error('Failed to load tags:', error);
      }
    };

    loadTags();
  }, []);

  // Додаємо ∅ лише для фільтрації
  const filterTags = useMemo(() => ['∅', ...tags.filter(t => t !== '∅')], [tags]);

  const handleTagChange = useCallback((tag) => {
    dispatch({ 
      type: ACTIONS.SET_SELECTED_TAGS, 
      payload: selectedTags.includes(tag)
        ? selectedTags.filter(t => t !== tag)
        : [...selectedTags, tag]
    });
  }, [dispatch, selectedTags]);

  const handleTagSelectForAssignment = useCallback((tag) => {
    dispatch({ type: ACTIONS.SET_SELECTED_TAG, payload: tag });
    dispatch({ type: ACTIONS.TOGGLE_SELECTION_MODE, payload: true });
    dispatch({ type: ACTIONS.SET_SELECTED_ITEMS, payload: [] });
  }, [dispatch]);

  const handleAddTag = useCallback((newTag) => {
    setTags((prevTags) => [...prevTags, newTag]);
  }, []);

  const handleUpdateTags = useCallback(async (selectedItems, selectedTag) => {
    if (selectedTag && selectedItems.length > 0) {
      try {
        await addTagToItems(selectedItems, selectedTag);
        const updatedTags = await fetchAllTags();
        setTags(updatedTags);
        dispatch({
          type: ACTIONS.SET_COLLECTIONS,
          payload: collections.map(item =>
            selectedItems.includes(item.id)
              ? { ...item, tags: Array.from(new Set([...(item.tags || []), selectedTag])) }
              : item
          )
        });
      } catch (error) {
        console.error('Failed to update tags:', error);
      } finally {
        dispatch({ type: ACTIONS.TOGGLE_SELECTION_MODE, payload: false });
        dispatch({ type: ACTIONS.SET_SELECTED_ITEMS, payload: [] });
        dispatch({ type: ACTIONS.SET_SELECTED_TAG, payload: null });
      }
    }
  }, [dispatch, collections]);

  return {
    tags: filterTags,
    handleTagChange,
    handleTagSelectForAssignment,
    handleAddTag,
    handleUpdateTags
  };
}

export default useTagsManager;