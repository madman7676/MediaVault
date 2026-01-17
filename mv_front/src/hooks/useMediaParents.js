import { useEffect } from "react";
import { fetchMediaParents } from "../api/mediaAPI";

// Custom hook для завантаження та обробки колекцій
function useMediaParents(setMediaList) {
  useEffect(() => {
    const fetchMediaList = async () => {
      console.log('Starting fetchMediaParents...');

      try {
        const mediaItems = await fetchMediaParents();
        console.log('Metadata fetched:', mediaItems);
        setMediaList(mediaItems);
      } catch (err) {
        console.error('Error fetching metadata:', err);
      } finally {
      }
    };

    fetchMediaList();
  }, [setMediaList]);
}

export default useMediaParents;