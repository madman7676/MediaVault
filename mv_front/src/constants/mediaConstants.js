// src/constants/mediaConstants.js
export const ACTIONS = {
    SET_COLLECTIONS: 'set_collections',
    SET_FILTERED_COLLECTIONS: 'set_filtered_collections',
    SET_FILTER: 'set_filter',
    SET_LOADING: 'set_loading',
    SET_ERROR: 'set_error',
    SET_SELECTED_TAGS: 'set_selected_tags',
    TOGGLE_TAG: 'toggle_tag',
    TOGGLE_SELECTED_ITEM: 'toggle_selected_item',
    TOGGLE_FILTER_MODE: 'toggle_filter_mode',
    TOGGLE_TAG_SETTINGS: 'toggle_tag_settings',
    TOGGLE_SELECTION_MODE: 'toggle_selection_mode',
    SET_SELECTED_ITEMS: 'set_selected_items',
    SET_SELECTED_TAG: 'set_selected_tag',
    TOGGLE_SETTINGS_MENU: 'toggle_settings_menu',
    TOGGLE_ONLINE_SERIES_DIALOG: 'toggle_online_series_dialog'
  };
  
  export const mediaTypeFilters = {
    ALL: 'all',
    MOVIE: 'movie',
    SERIES: 'series',
    ONLINE_SERIES: 'online_series',
    SERIES_COMBINED: 'series_combined'
  };
  
  export const initialState = {
    collections: [],
    filteredCollections: [],
    filter: 'all',
    loading: true,
    error: null,
    selectedTags: [],
    filterMode: 'include',
    openTagSettings: false,
    selectionMode: false,
    selectedItems: [],
    selectedTag: null,
    openSettingsMenu: false,
    openOnlineSeriesDialog: false
  };