import { ACTIONS } from '../constants/mediaConstants';

// Редуктор для управління станом
function mediaReducer(state, action) {
  switch (action.type) {
    case ACTIONS.TOGGLE_SELECTED_ITEM:
        const itemId = action.payload;
        return { 
            ...state, 
            selectedItems: state.selectedItems.includes(itemId) 
            ? state.selectedItems.filter(id => id !== itemId) 
            : [...state.selectedItems, itemId]
        };
    case ACTIONS.SET_FILTERED_COLLECTIONS:
        return { ...state, filteredCollections: action.payload };
    case ACTIONS.SET_COLLECTIONS:
      return { ...state, collections: action.payload, filteredCollections: action.payload };
    case ACTIONS.SET_FILTER:
      return { ...state, filter: action.payload };
    case ACTIONS.SET_LOADING:
      return { ...state, loading: action.payload };
    case ACTIONS.SET_ERROR:
      return { ...state, error: action.payload };
    case ACTIONS.SET_SELECTED_TAGS:
      return { ...state, selectedTags: action.payload };
    case ACTIONS.TOGGLE_FILTER_MODE:
      return { ...state, filterMode: state.filterMode === 'include' ? 'exclude' : 'include' };
    case ACTIONS.TOGGLE_TAG_SETTINGS:
      return { ...state, openTagSettings: !state.openTagSettings };
    case ACTIONS.TOGGLE_SELECTION_MODE:
      return { 
        ...state, 
        selectionMode: action.payload, 
        selectedItems: action.payload ? state.selectedItems : [] 
      };
    case ACTIONS.SET_SELECTED_ITEMS:
      return { ...state, selectedItems: action.payload };
    case ACTIONS.SET_SELECTED_TAG:
      return { ...state, selectedTag: action.payload };
    case ACTIONS.TOGGLE_SETTINGS_MENU:
      return { ...state, openSettingsMenu: !state.openSettingsMenu };
    case ACTIONS.TOGGLE_ONLINE_SERIES_DIALOG:
      return { ...state, openOnlineSeriesDialog: !state.openOnlineSeriesDialog };
    default:
      return state;
  }
}

export default mediaReducer;