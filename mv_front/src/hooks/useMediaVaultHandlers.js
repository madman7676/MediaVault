import { useCallback } from "react";

import { ACTIONS } from '../constants/mediaConstants';

export const useMediaVaultHandlers = (dispatch) => {
    
    // Обробники подій з useCallback
    const handleFilterChange = useCallback((newFilter) => {
    dispatch({ type: ACTIONS.SET_FILTER, payload: newFilter });
    }, [dispatch]);

    const toggleFilterMode = useCallback(() => {
    dispatch({ type: ACTIONS.TOGGLE_FILTER_MODE });
    }, [dispatch]);

    const handleTagSettings = useCallback(() => {
    dispatch({ type: ACTIONS.TOGGLE_TAG_SETTINGS });
    dispatch({ type: ACTIONS.TOGGLE_SETTINGS_MENU });
    }, [dispatch]);

    const handleOpenOnlineSeriesDialog = useCallback(() => {
    dispatch({ type: ACTIONS.TOGGLE_ONLINE_SERIES_DIALOG });
    dispatch({ type: ACTIONS.TOGGLE_SETTINGS_MENU });
    }, [dispatch]);

    const handleItemSelection = useCallback((id) => {
    dispatch({
        type: ACTIONS.TOGGLE_SELECTED_ITEM,
        payload: id
    });
    }, [dispatch]);

    return {
        handleFilterChange,
        toggleFilterMode,
        handleTagSettings,
        handleOpenOnlineSeriesDialog,
        handleItemSelection
    };
};