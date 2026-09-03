import { useEffect } from "react";
import { ACTIONS } from '../constants/mediaConstants';
import { fetchMedia } from '../api/mediaAPI';
import { fetchMovies } from '../api/movieAPI';
import { fetchSeries } from '../api/seriesAPI';

// Custom hook для завантаження та обробки колекцій
function useCollectionsLoader(dispatch, filterType, filterTags, filterMode) {
  useEffect(() => {
    const fetchCollections = async () => {
      console.log('Starting fetchCollections...');

      try {
        dispatch({ type: ACTIONS.SET_LOADING, payload: true });

        let mediaItems = [];
        switch (filterType) {
          case 'movies':
            mediaItems = await fetchMovies(filterTags, filterMode);
            break;
          case 'series':
            mediaItems = await fetchSeries(filterTags, filterMode);
            break;
          default:
            mediaItems = await fetchMedia(filterTags, filterMode);
        }
        console.log('Metadata fetched:', mediaItems);

        dispatch({ type: ACTIONS.SET_COLLECTIONS, payload: mediaItems });
      } catch (err) {
        console.error('Error fetching metadata:', err);
        dispatch({ type: ACTIONS.SET_ERROR, payload: 'Failed to load collections. Please check the API connection.' });
      } finally {
        dispatch({ type: ACTIONS.SET_LOADING, payload: false });
      }
    };

    fetchCollections();
  }, [dispatch, filterType, filterTags, filterMode]);
}

export default useCollectionsLoader;