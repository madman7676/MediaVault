import { useEffect, useCallback, useReducer } from 'react';
import { 
  CssBaseline, 
  ThemeProvider,
  Box
} from '@mui/material';

import darkTheme from '../styles/theme/darkTheme';
import MVLogo from '../images/MV_Logo2.png';
import background from '../images/background.png';

import TagFilter from '../components/Main/TagFilter';
import TagSettings from '../components/Main/TagSettings';
import TypeFilterButtons from '../components/Main/TypeFilterButtons';
import OnlineSeriesDialog from '../components/Main/OnlineSeriesDialog';
import { initialState, ACTIONS } from '../constants/mediaConstants';
import Bookmarks from '../components/Main/Bookmarks';
import GridCollection from '../components/Main/GridCollection';
import SettingsFloatButton from '../components/Main/SettingsFloatButton';

import mediaReducer from '../hooks/useMediaReducer';
import useOnlineSeriesForm from '../hooks/useOnlineSeriesForm';
import useCollectionsLoader from '../hooks/useCollectionsLoader';
import useTagsManager from '../hooks/useTagsManager';
import { useMediaVaultHandlers } from '../hooks/useMediaVaultHandlers';
import { useCollectionFiltering } from '../hooks/useCollectionFilltering';
import { useLetterNavigation } from '../hooks/useLetterNavigation';
import useLocalStorage from '../hooks/useLocalStorage';


const MediaVault = () => {
  
  const { getInitialFilter, getInitialTags, saveToLocalStorage } = useLocalStorage(initialState);

  // Використовуємо useReducer замість multiple useState
  const [state, dispatch] = useReducer(mediaReducer, {
    ...initialState,
    filter: getInitialFilter(),
    selectedTags: getInitialTags(),
  });

  // Зберігаємо в localStorage при зміні state
  useEffect(() => {
    saveToLocalStorage(state.filter, state.selectedTags);
  }, [state.filter, state.selectedTags, saveToLocalStorage]);

  const {
    collections, filteredCollections, filter, loading, error,
    selectedTags, filterMode, openTagSettings, selectionMode,
    selectedItems, selectedTag, openSettingsMenu, openOnlineSeriesDialog
  } = state;

  // Використовуємо custom hooks
  const {
    handleFilterChange,
    toggleFilterMode,
    handleTagSettings,
    handleOpenOnlineSeriesDialog,
    handleItemSelection
  } = useMediaVaultHandlers(dispatch);

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
  } = useTagsManager(dispatch, selectedTags, collections);

  const handleClearTags = useCallback(() => {
    dispatch({ type: ACTIONS.SET_SELECTED_TAGS, payload: [] });
  }, []);

  useCollectionFiltering(collections, filter, selectedTags, filterMode, dispatch);

  // Обробники подій з useCallback
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

  const { letters, letterRefs, scrollToLetter } = useLetterNavigation(filteredCollections);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>{error}</div>;

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', flexDirection: 'row' }}> 
        {/* Основний контент */}
        <Box sx={{ flexGrow: 1, position: 'relative'}}>
          
          <div className="media-vault-container" style={{
            padding: '1rem 2rem',
            position: 'relative',
            backgroundImage: `url(${background})`,
            backgroundRepeat: 'repeat',
            minHeight: '100vh'
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
              
              <TypeFilterButtons filter={filter} handleFilterChange={handleFilterChange} />
              
            </header>
            <Box sx={{display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              backgroundColor: 'rgba(0, 0, 0, 0.5)',
            }}>
              <TagFilter
                tags={tags}
                selectedTags={selectedTags}
                handleTagChange={handleTagChange}
                filterMode={filterMode}
                toggleFilterMode={toggleFilterMode}
                handleClearTags={handleClearTags}
              />
              {/* <SortingButtons sortBy={null} setSortBy={null} /> */}
            </Box>
            <Bookmarks letters={letters} onLetterClick={scrollToLetter} />
            
            <GridCollection
              openTagSettings={openTagSettings}
              filteredCollections={filteredCollections}
              letterRefs={letterRefs}
              selectionMode={selectionMode}
              selectedItems={selectedItems}
              handleItemSelection={handleItemSelection} 
            />

            <SettingsFloatButton 
              onClickSettingsButton={() => dispatch({ type: ACTIONS.TOGGLE_SETTINGS_MENU })}
              openSettingsMenu={openSettingsMenu}
              handleTagSettings={handleTagSettings}
              handleOpenOnlineSeriesDialog={handleOpenOnlineSeriesDialog}
            />

            {openTagSettings && (
              <TagSettings
                tags={tags}
                onAddTag={handleAddTag}
                onUpdateTags={() => handleUpdateTags(selectedItems, selectedTag)}
                selectedTag={selectedTag}
                setSelectedTag={handleTagSelectForAssignment}
                selectedItems={selectedItems}
                setSelectionMode={(val) => dispatch({ type: ACTIONS.TOGGLE_SELECTION_MODE, payload: val })}
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
        </Box>
      </Box>
    </ThemeProvider>
  );
};

export default MediaVault;