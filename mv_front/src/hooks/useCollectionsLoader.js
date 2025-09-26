import { useEffect } from "react";
import { ACTIONS } from '../constants/mediaConstants';
import { fetchMetadata } from '../api/metadataAPI';
import { fetchThumbnail } from '../api/thumbnailAPI';

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

export default useCollectionsLoader;