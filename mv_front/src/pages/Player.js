// Player.js component for displaying video and collection/season files
import 'videojs-hotkeys';
import config from '../config.json';
import palette from '../styles/theme/palette';
import FileList from '../components/FileList';
import PlayerControls from '../components/Player/PlayerControls';
import { Settings, CheckBox, CheckBoxOutlineBlank } from '@mui/icons-material';
import React, { useState, useEffect, useRef } from 'react';
import { Box, Typography, Menu, MenuItem, Checkbox, IconButton } from '@mui/material';
import { useParams } from 'react-router-dom';
import { fetchMetadataById, fetchTimeToSkip, updateTimeToSkip } from '../api/metadataAPI';

const Player = () => {
    const [fileList, setFileList] = useState([]);
    const [title, setTitle] = useState('');
    const [currentFile, setCurrentFile] = useState(null);
    const currentTimeToSkipRef = useRef([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [openSeasons, setOpenSeasons] = useState({});
    const [skipTimeEnabled, setSkipTimeEnabled] = useState(true);
    const { itemId } = useParams();
    const allPaths = useRef([]);
    const currentPath = useRef(null);

    const handleToggleSkipTime = () => {
        setSkipTimeEnabled((prev) => !prev);
    };

    function getLastIntFromString(input) {
        const parts = input.trim().split(/\s+/); // Розбиваємо рядок на частини
        const lastPart = parts[parts.length - 1]; // Беремо останню частину
    
        const parsedValue = parseInt(lastPart, 10); // Пробуємо перетворити в int
        return isNaN(parsedValue) ? 1 : parsedValue; // Перевіряємо, чи вдалося
    }

    const getCurrentPath = (itemList, itemName) => {
        if (!itemList || !itemList.item || !itemList.item.path || !itemList.item.seasons) {
            return null; // Перевірка на валідність структури
        }
    
        for (const season of itemList.item.seasons) {
            for (const file of season.files) {
                if (file.name === itemName) {
                    return itemList.item.path; // Повертаємо path, якщо знайдено
                }
            }
        }
    
        return null; // Якщо файл не знайдено
    };

    const findFileName = (url) => {
        if (!url) return null;
        for (const season of fileList) {
            for (const file of season.files) {
                if (file.url === url) {
                    return file.name;
                }
            }
        }
        return null; // Якщо URL не знайдено
    }

    const processFiles = (item) => {
        if (item.type === 'series') {
            return item.seasons.map((season, seasonIndex) => ({
                seasonTitle: `Сезон ${seasonIndex + 1}`,
                files: season.files.map(file => ({
                    url: `${config.API_BASE_URL}/api/video?path=${encodeURIComponent(season.path + '/' + file.name)}`,
                    name: file.name,
                    timeToSkip: file.timeToSkip || [],
                })),
            }));
        }
        return [{
            seasonTitle: 'Collection',
            files: item.parts.map(part => ({
                url: `${config.API_BASE_URL}/api/video?path=${encodeURIComponent(part.path)}`,
                name: part.title,
                timeToSkip: part.timeToSkip || [],
            })),
        }];
    };

    const handleVideoEnd = () => {
        const flatFileList = fileList.flatMap(season => season.files);
        const currentIndex = flatFileList.findIndex(file => file.url === currentFile);

        if (currentIndex !== -1 && currentIndex < flatFileList.length - 1) {
            const nextFile = flatFileList[currentIndex + 1];
            if (nextFile) {
                handleFetchTimeToSkip(currentPath.current, nextFile.name);
                currentTimeToSkipRef.current = nextFile.timeToSkip || [];

                setCurrentFile(nextFile.url);
                saveLastWatched(itemId, nextFile.url);
            }
        }
    };

    const fetchMetadata = async () => {
        try {
            const item = await fetchMetadataById(itemId);
            setTitle(item.title || 'Files');
            setFileList(processFiles(item));
            if (item.type === 'series' && Array.isArray(item.seasons)) {
                allPaths.current = item.seasons.map(season => season.path);
            } else if (item.type === 'movie' && Array.isArray(item.parts)) {
                allPaths.current = item.parts.map(part => part.path);
            } else {
                allPaths.current = [];
            }
            // allPaths.current=item.seasons.map(season => season.path);
        } catch (err) {
            setError(`Error fetching metadata: ${err.message}`);
        } finally {
            setLoading(false);
        }
    };

    const handleFetchTimeToSkip = async (path, name) => {
        try {
            console.log('Fetching timeToSkip for:', { path, name }); // Логування
            const timeToSkip = await fetchTimeToSkip(path, name);
            console.log('Fetched timeToSkip:', timeToSkip);
            currentTimeToSkipRef.current = timeToSkip;
        } catch (error) {
            console.error(`Error fetching timeToSkip: ${error.message}`);
        }
    };

    const handleUpdateTimeToSkip = async (updatedTimeToSkip) => {
        try {
            await updateTimeToSkip(currentFile, itemId, updatedTimeToSkip);
            currentTimeToSkipRef.current = updatedTimeToSkip;
            console.log('timeToSkip updated successfully');
        } catch (error) {
            console.error(`Error updating timeToSkip: ${error.message}`);
        }
    };

    // Зберігаємо lastWatched як об'єкт з itemId як ключем
    const saveLastWatched = (itemId, fileUrl) => {
        const lastWatchedAll = JSON.parse(localStorage.getItem('lastWatchedAll')) || {};
        lastWatchedAll[itemId] = { fileUrl };
        localStorage.setItem('lastWatchedAll', JSON.stringify(lastWatchedAll));
    };

    const getLastWatched = (itemId) => {
        const lastWatchedAll = JSON.parse(localStorage.getItem('lastWatchedAll')) || {};
        return lastWatchedAll[itemId]?.fileUrl;
    };

    const handleSelectFile = (url) => {
        const selectedFileMetadata = fileList
            .flatMap(season => {
                if (season.files.some(file=>file.url === url)) currentPath.current=allPaths.current[(getLastIntFromString(season.seasonTitle)-1)];
                return season.files;
            })
            .find(file => file.url === url);

        if (selectedFileMetadata) {
            handleFetchTimeToSkip(currentPath.current, selectedFileMetadata.name);
        }
        setCurrentFile(url);
        saveLastWatched(itemId, url);
    };

    useEffect(() => {
        document.body.style.margin = '0';
        fetchMetadata();
    }, [itemId]);

    useEffect(() => {
        const lastFileUrl = getLastWatched(itemId);
        if (lastFileUrl && fileList.length > 0) {
            // ...existing code, заміни lastWatched.fileUrl на lastFileUrl...
            const flatFileList = fileList.flatMap(season => season.files);
            const lastFile = flatFileList.find(file => file.url === lastFileUrl);
            if (lastFile) {
                const seasonIndex = fileList.findIndex(season =>
                    season.files.some(file => file.url === lastFileUrl)
                );
                if (seasonIndex >= 0) {
                    setOpenSeasons(prev => ({ ...prev, [seasonIndex]: true }));
                }
            }
        }
    }, [fileList]);

    const handleToggleSeason = (seasonIndex) => {
        setOpenSeasons(prev => ({
            ...prev,
            [seasonIndex]: !prev[seasonIndex],
        }));
    };

    const playerBoxRef = useRef(null);

    const focusPlayer = () => {
        if (playerBoxRef.current) {
            playerBoxRef.current.focus();
        }
    };

    useEffect(() => {
        focusPlayer();
    }, []);

    if (loading) return <Typography>Loading...</Typography>;
    if (error) return <Typography color="error">{error}</Typography>;

    return (
        <Box sx={{ display: 'flex', flexDirection: 'row', height: '100vh', width: '100vw', backgroundColor: palette.background.page, overflow: 'hidden' }}>
            <Box
                sx={{
                    flex: 3,
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    backgroundColor: palette.background.dark,
                    padding: 2,
                }}
            >
                <PlayerControls
                    onBlur={focusPlayer}
                    ref={playerBoxRef}
                    currentFile={currentFile}
                    currentName={findFileName(currentFile)}
                    currentPath={currentPath.current}
                    // currentTimeToSkip={currentTimeToSkipRef.current}
                    skipTimeEnabled={skipTimeEnabled}
                    handleVideoEnd={handleVideoEnd}
                />
            </Box>

            <Box
                sx={{
                    flex: 1,
                    overflowY: 'auto',
                    borderLeft: 'none',
                    padding: 2,
                    backgroundColor: palette.background.card,
                    '::-webkit-scrollbar': { display: 'none' },
                    '-ms-overflow-style': 'none',
                    'scrollbar-width': 'none',
                }}
            >
                <FileList
                    itemId={itemId}
                    fileList={fileList}
                    currentFile={currentFile}
                    currentTitle={title}
                    openSeasons={openSeasons}
                    handleToggleSeason={handleToggleSeason}
                    handleSelectFile={handleSelectFile}
                    palette={palette}
                    lastWatched={getLastWatched(itemId)}
                />
            </Box>
        </Box>
    );
};

export default Player;
