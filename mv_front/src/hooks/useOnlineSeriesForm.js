import { useState, useCallback } from "react";

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

export default useOnlineSeriesForm;