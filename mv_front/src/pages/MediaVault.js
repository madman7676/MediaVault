import React, { useState, useEffect, useMemo, useCallback, useReducer } from 'react';
import CatalogCard from '../components/CatalogCard';
import { fetchMetadata, addTagToItems, fetchAllTags } from '../api/metadataAPI';
import { fetchThumbnail } from '../api/thumbnailAPI';
import TagFilter from '../components/TagFilter';
import { 
  Grid2 as Grid, 
  SpeedDial, 
  SpeedDialAction, 
  CssBaseline, 
  ThemeProvider, 
  createTheme, 
  ButtonGroup, 
  Button, 
  MenuItem 
} from '@mui/material';
import BookmarksIcon from '@mui/icons-material/Bookmarks';
import AddIcon from '@mui/icons-material/Add';
import SettingsIcon from '@mui/icons-material/Settings';
import TagSettings from '../components/TagSettings';
import palette from '../styles/theme/palette';
import MVLogo from '../images/MV_Logo2.png';
import background from '../images/background.png';
import OnlineSeriesDialog from '../components/OnlineSeriesDialog';
import { mediaTypeFilters, initialState, ACTIONS } from '../constants/mediaConstants';

// Створюємо тему один раз за межами компонента
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    background: {
      default: palette.background.page,
      paper: palette.background.paper,
    },
    text: {
      primary: palette.text.lightPrimary,
      secondary: palette.text.lightSecondary,
    },
  },
});

// Редуктор для управління станом
function reducer(state, action) {
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

// Custom hook для управління серіями
function useOnlineSeriesForm() {
  const [formData, setFormData] = useState({
    title: '',
    imageUrl: '',
    seasons: [{ name: 'Сезон 1', episodes: '' }]
  });

  const updateTitle = useCallback((value) => {
    setFormData(prev => ({ ...prev, title: value }));
  }, []);

  const updateImageUrl = useCallback((value) => {
    setFormData(prev => ({ ...prev, imageUrl: value }));
  }, []);

  const updateSeasonName = useCallback((index, value) => {
    setFormData(prev => {
      const updatedSeasons = [...prev.seasons];
      updatedSeasons[index].name = value;
      return { ...prev, seasons: updatedSeasons };
    });
  }, []);

  const updateSeasonEpisodes = useCallback((index, value) => {
    setFormData(prev => {
      const updatedSeasons = [...prev.seasons];
      updatedSeasons[index].episodes = value;
      return { ...prev, seasons: updatedSeasons };
    });
  }, []);

  const addSeason = useCallback(() => {
    setFormData(prev => ({
      ...prev,
      seasons: [...prev.seasons, { name: `Сезон ${prev.seasons.length + 1}`, episodes: '' }]
    }));
  }, []);

  const removeSeason = useCallback((index) => {
    setFormData(prev => ({
      ...prev,
      seasons: prev.seasons.filter((_, i) => i !== index)
    }));
  }, []);

  const resetForm = useCallback(() => {
    setFormData({
      title: '',
      imageUrl: '',
      seasons: [{ name: 'Сезон 1', episodes: '' }]
    });
  }, []);

  return {
    formData,
    updateTitle,
    updateImageUrl,
    updateSeasonName,
    updateSeasonEpisodes,
    addSeason,
    removeSeason,
    resetForm
  };
}

// Custom hook для завантаження та обробки колекцій
function useCollectionsLoader(dispatch) {
  useEffect(() => {
    const fetchCollections = async () => {
      console.log('Starting fetchCollections...');
      try {
        dispatch({ type: ACTIONS.SET_LOADING, payload: true });
        const data = await fetchMetadata();
        console.log('Metadata fetched:', data);
        const { movies = [], series = [], online_series = [] } = data;

        // Функція обробки колекції
        const processCollection = async (item, type) => {
          try {
            let thumbnailUrl = '';
            if (type === 'online_series') {
              thumbnailUrl = item.image_url;
            } else {
              thumbnailUrl = await fetchThumbnail(item.path);
            }
            
            return {
              id: item.id,
              title: type === 'movie' ? item.title.replace(/\.[^/.]+$/, "") : item.title,
              type,
              partsCount: type === 'movie' ? item.parts.length : item.seasons.length,
              thumbnailUrl,
              tags: item.tags || [],
            };
          } catch (err) {
            console.error(`Failed to fetch thumbnail for ${type} ${item.title}:`, err);
            return {
              id: item.id,
              title: type === 'movie' ? item.title.replace(/\.[^/.]+$/, "") : item.title,
              type,
              partsCount: type === 'movie' ? item.parts.length : item.seasons.length,
              thumbnailUrl: '',
              tags: item.tags || [],
            };
          }
        };

        // Обробляємо всі типи колекцій паралельно
        const [movieCollections, seriesCollections, onlineSeriesCollections] = await Promise.all([
          Promise.all(movies.map(movie => processCollection(movie, 'movie'))),
          Promise.all(series.map(serie => processCollection(serie, 'series'))),
          Promise.all(online_series.map(onlineSerie => processCollection(onlineSerie, 'online_series')))
        ]);

        const allCollections = [...movieCollections, ...seriesCollections, ...onlineSeriesCollections];
        dispatch({ type: ACTIONS.SET_COLLECTIONS, payload: allCollections });
      } catch (err) {
        console.error('Error fetching metadata:', err);
        dispatch({ type: ACTIONS.SET_ERROR, payload: 'Failed to load collections. Please check the API connection.' });
      } finally {
        dispatch({ type: ACTIONS.SET_LOADING, payload: false });
      }
    };

    fetchCollections();
  }, [dispatch]);
}

// Custom hook для тегів
function useTagsManager(dispatch, selectedTags) {
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
      } catch (error) {
        console.error('Failed to update tags:', error);
      } finally {
        dispatch({ type: ACTIONS.TOGGLE_SELECTION_MODE, payload: false });
        dispatch({ type: ACTIONS.SET_SELECTED_ITEMS, payload: [] });
        dispatch({ type: ACTIONS.SET_SELECTED_TAG, payload: null });
      }
    }
  }, [dispatch]);

  return {
    tags,
    handleTagChange,
    handleTagSelectForAssignment,
    handleAddTag,
    handleUpdateTags
  };
}

const MediaVault = () => {
  // Використовуємо useReducer замість multiple useState
  const [state, dispatch] = useReducer(reducer, initialState);
  const {
    collections, filteredCollections, filter, loading, error,
    selectedTags, filterMode, openTagSettings, selectionMode,
    selectedItems, selectedTag, openSettingsMenu, openOnlineSeriesDialog
  } = state;

  // Використовуємо custom hooks
  const {
    formData,
    updateTitle,
    updateImageUrl,
    updateSeasonName,
    updateSeasonEpisodes,
    addSeason,
    removeSeason,
    resetForm
  } = useOnlineSeriesForm();

  // Завантажуємо колекції
  useCollectionsLoader(dispatch);

  // Управління тегами
  const {
    tags,
    handleTagChange,
    handleTagSelectForAssignment,
    handleAddTag,
    handleUpdateTags
  } = useTagsManager(dispatch, selectedTags);

  // Фільтрація колекцій з використанням useMemo
  const filteredResults = useMemo(() => {
    let filtered = collections;

    if (filter !== 'all') {
      if (filter === 'series_combined') {
        filtered = filtered.filter(collection => 
          collection.type === 'series' || collection.type === 'online_series');
      } else {
        filtered = filtered.filter(collection => collection.type === filter);
      }
    }

    if (selectedTags && selectedTags.length > 0) {
      if (filterMode === 'include') {
        filtered = filtered.filter(collection => 
            collection.tags && selectedTags.some(tag => collection.tags.includes(tag)));
      } else {
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
  }, [filteredResults]);

  // Обробники подій з useCallback
  const handleFilterChange = useCallback((newFilter) => {
    dispatch({ type: ACTIONS.SET_FILTER, payload: newFilter });
  }, []);

  const toggleFilterMode = useCallback(() => {
    dispatch({ type: ACTIONS.TOGGLE_FILTER_MODE });
  }, []);

  const handleTagSettings = useCallback(() => {
    dispatch({ type: ACTIONS.TOGGLE_TAG_SETTINGS });
    dispatch({ type: ACTIONS.TOGGLE_SETTINGS_MENU });
  }, []);

  const handleOpenOnlineSeriesDialog = useCallback(() => {
    dispatch({ type: ACTIONS.TOGGLE_ONLINE_SERIES_DIALOG });
    dispatch({ type: ACTIONS.TOGGLE_SETTINGS_MENU });
  }, []);

  const handleCloseOnlineSeriesDialog = useCallback(() => {
    dispatch({ type: ACTIONS.TOGGLE_ONLINE_SERIES_DIALOG });
    resetForm();
  }, [resetForm]);

  const handleSaveOnlineSeries = useCallback(() => {
    console.log('Saving online series:', {
      title: formData.title,
      imageUrl: formData.imageUrl,
      seasons: formData.seasons.map((season) => ({
        name: season.name,
        episodes: season.episodes.split('\n').map((url) => url.trim()).filter(Boolean),
      })),
    });
    handleCloseOnlineSeriesDialog();
  }, [formData, handleCloseOnlineSeriesDialog]);

  const handleItemSelection = useCallback((id) => {
    dispatch({
      type: ACTIONS.TOGGLE_SELECTED_ITEM,
      payload: id
    });
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>{error}</div>;

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <div className="media-vault-container" style={{ 
        padding: '1rem 2rem', 
        position: 'relative', 
        backgroundImage: `url(${background})`, 
        backgroundRepeat: 'repeat' 
      }}>
        <header className="media-vault-header">
          <img 
            src={MVLogo} 
            alt="MediaVault Logo" 
            className="media-vault-logo" 
            style={{ 
              display: 'inline-block', 
              marginRight: '1rem', 
              height: '100px' 
            }} 
          />
          
          <ButtonGroup 
            variant="contained" 
            className="filter-buttons" 
            style={{ 
              marginBottom: '1rem', 
              float: 'right', 
              backgroundColor: 'rgba(0, 0, 0, 0.5)' 
            }}
          >
            <Button 
              onClick={() => handleFilterChange('all')} 
              color={filter === 'all' ? 'primary' : 'default'}
            >
              All
            </Button>
            <Button 
              onClick={() => handleFilterChange('movie')} 
              color={filter === 'movie' ? 'primary' : 'default'}
            >
              Movies
            </Button>
            <Button 
              onClick={() => handleFilterChange('series_combined')}
              color={
                filter === 'series_combined' || 
                filter === 'series' || 
                filter === 'online_series' ? 'primary' : 'default'
              }
            >
              Series
            </Button>
          </ButtonGroup>
          
          {filter === 'series_combined' && (
            <div className="series-submenu" style={{ 
              position: 'absolute', 
              top: '3.39rem', 
              right: '2.25rem', 
              backgroundColor: 'rgba(0, 0, 0, 0.5)' 
            }}>
              <MenuItem onClick={() => handleFilterChange('series')}>Local</MenuItem>
              <MenuItem onClick={() => handleFilterChange('online_series')}>Online</MenuItem>
            </div>
          )}
        </header>

        <TagFilter
          tags={tags}
          selectedTags={selectedTags}
          handleTagChange={handleTagChange}
          filterMode={filterMode}
          toggleFilterMode={toggleFilterMode}
        />

        <Grid 
          container 
          spacing={2} 
          justifyContent="center" 
          style={{ justifyContent: openTagSettings ? 'left' : 'center' }}
        >
          {filteredCollections.map(collection => (
            <Grid item xs={12} sm={6} md={4} key={collection.id}>
              <CatalogCard 
                title={collection.title} 
                type={collection.type} 
                partsCount={collection.partsCount} 
                thumbnailUrl={collection.thumbnailUrl} 
                link={'/player/' + collection.id}
                showCheckbox={selectionMode}
                isSelected={selectedItems.includes(collection.id)}
                onSelect={() => handleItemSelection(collection.id)}
              />
            </Grid>
          ))}
        </Grid>

        <SpeedDial
          ariaLabel="Settings"
          icon={<SettingsIcon />}
          direction="up"
          onClick={() => dispatch({ type: ACTIONS.TOGGLE_SETTINGS_MENU })}
          open={openSettingsMenu}
          className="settings-dial"
          style={{ position: 'fixed', bottom: '2rem', right: '2rem' }}
        >
          <SpeedDialAction
            icon={<BookmarksIcon />}
            tooltipTitle="Tag Settings"
            onClick={handleTagSettings}
          />
          <SpeedDialAction
            icon={<AddIcon />}
            tooltipTitle="Add Online Series"
            onClick={handleOpenOnlineSeriesDialog}
          />
        </SpeedDial>

        {openTagSettings && (
          <TagSettings
            tags={tags}
            onAddTag={handleAddTag}
            onUpdateTags={() => handleUpdateTags(selectedItems, selectedTag)}
            selectedTag={selectedTag}
            setSelectedTag={handleTagSelectForAssignment}
            selectedItems={selectedItems}
          />
        )}

        <OnlineSeriesDialog 
          open={openOnlineSeriesDialog}
          onClose={handleCloseOnlineSeriesDialog}
          title={formData.title}
          onTitleChange={updateTitle}
          imageUrl={formData.imageUrl}
          onImageUrlChange={updateImageUrl}
          seasons={formData.seasons}
          onUpdateSeasonName={updateSeasonName}
          onUpdateSeasonEpisodes={updateSeasonEpisodes}
          onAddSeason={addSeason}
          onRemoveSeason={removeSeason}
          onSave={handleSaveOnlineSeries}
        />
      </div>
    </ThemeProvider>
  );
};

export default MediaVault;