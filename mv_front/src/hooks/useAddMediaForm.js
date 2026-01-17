import { useState, useCallback } from "react";

// Custom hook для управління серіями
function useAddMediaForm() {
    const [formData, setFormData] = useState({
        title: "",
        selectedFolderPath: "",
        isNewMedia: true,
        isSeries: true,
        selectedMedia: "",
    });

    const updateTitle = useCallback((value) => {
        setFormData(prev => ({ ...prev, title: value }));
    }, []);

    const updateSelectedFolderPath = useCallback((value) => {
        setFormData(prev => ({ ...prev, selectedFolderPath: value }));
    }, []);

    const updateIsNewMedia = useCallback((value) => {
        setFormData(prev => ({ ...prev, isNewMedia: value }));
    }, []);

    const updateIsSeries = useCallback((value) => {
        setFormData(prev => ({ ...prev, isSeries: value }));
    }, []);

    const updateSelectedMedia = useCallback((value) => {
        setFormData(prev => ({ ...prev, selectedMedia: value }));
    }, []);

    const resetForm = useCallback(() => {
        setFormData({
            title: "",
            selectedFolderPath: "",
            isNewMedia: true,
            isSeries: true,
            selectedMedia: "",
        });
    }, []);

  return {
    formData,
    updateTitle,
    updateSelectedFolderPath,
    updateIsNewMedia,
    updateIsSeries,
    updateSelectedMedia,
    resetForm
  };
}

export default useAddMediaForm;