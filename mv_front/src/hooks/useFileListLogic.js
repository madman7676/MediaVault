// useFileListLogic.js: Hook for managing file list logic
import { useState, useMemo } from 'react';

const useFileListLogic = (metadata, onSelectFile) => {
    const [openSeasons, setOpenSeasons] = useState({});

    const fileList = useMemo(() => {
        if (!metadata) return [];

        if (metadata.type === 'series') {
            return metadata.seasons.map((season, seasonIndex) => ({
                seasonTitle: `Сезон ${seasonIndex + 1}`,
                files: season.files.map(file => ({
                    url: file.url,
                    name: file.name,
                    timeToSkip: file.timeToSkip || [],
                })),
            }));
        }

        return [{
            seasonTitle: 'Collection',
            files: metadata.parts.map(part => ({
                url: part.url,
                name: part.title,
                timeToSkip: part.timeToSkip || [],
            })),
        }];
    }, [metadata]);

    const handleToggleSeason = (seasonIndex) => {
        setOpenSeasons(prev => ({
            ...prev,
            [seasonIndex]: !prev[seasonIndex],
        }));
    };

    const handleSelectFile = (url) => {
        if (onSelectFile) {
            onSelectFile(url);
        }
    };

    return {
        fileList,
        openSeasons,
        handleToggleSeason,
        handleSelectFile,
    };
};

export default useFileListLogic;
