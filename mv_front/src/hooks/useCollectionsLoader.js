import { useEffect } from "react";
import { ACTIONS } from '../constants/mediaConstants';
import { fetchAllMedia } from '../api/mediaAPI';
import { fetchThumbnail } from '../api/thumbnailAPI';

// Custom hook для завантаження та обробки колекцій
function useCollectionsLoader(dispatch) {
  useEffect(() => {
    const fetchCollections = async () => {
      console.log('Starting fetchCollections...');
      try {
        dispatch({ type: ACTIONS.SET_LOADING, payload: true });
        const allMediaItems = await fetchAllMedia();
        console.log('Metadata fetched:', allMediaItems);

        // Функція додати мініатюру до елемента
        // const addThumbnail = async (item) => {

        //   try {
        //     let thumbnailUrl = '';
        //     thumbnailUrl = await fetchThumbnail(item.path);
            
        //     return { ...item, thumbnailUrl: thumbnailUrl };
        //   } catch (thumbError) {
        //     console.error(`Failed to fetch thumbnail for ${item.path}:`, thumbError);
        //     return { ...item, thumbnailUrl: '' }; // Повертаємо без мініатюри у випадку помилки
        //   }
        // };

        // Обробляємо всі типи колекцій паралельно
        const mediaCollections = await Promise.all(allMediaItems);

        dispatch({ type: ACTIONS.SET_COLLECTIONS, payload: mediaCollections });
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