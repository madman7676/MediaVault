// Player.js component for displaying video and collection/season files
import 'videojs-hotkeys';
import config from '../config.json';
import palette from '../styles/theme/palette';
import FileList from '../components/Player/FileList';
import PlayerControls from '../components/Player/PlayerControls';
import { Settings, CheckBox, CheckBoxOutlineBlank } from '@mui/icons-material';
import React, { useState, useEffect, useRef } from 'react';
import { Box, Typography, Menu, MenuItem, Checkbox, IconButton } from '@mui/material';
import { useParams } from 'react-router-dom';
import { fetchMetadataById, fetchTimeToSkip, updateTimeToSkip } from '../api/metadataAPI';
import { fetchMediaById } from '../api/mediaAPI';
import { fetchSeriesSeasonsAndEpisodesById } from '../api/seriesAPI';
import { fetchMovieItemsById } from '../api/movieAPI';
import { fetchDefaultBookmarks } from '../api/bookmarksAPI';


// Зберігаємо lastWatched в localStorage
const saveLastWatched = (mediaId, currentFile) => {
    const lastWatchedAll = JSON.parse(localStorage.getItem('lastWatchedAll')) || {};
    lastWatchedAll[mediaId] = currentFile;
    localStorage.setItem('lastWatchedAll', JSON.stringify(lastWatchedAll));
};
const getLastWatched = (mediaId) => {
    const lastWatchedAll = JSON.parse(localStorage.getItem('lastWatchedAll')) || {};
    return lastWatchedAll[mediaId] || null;
};

const Player = () => {
    const [fileList, setFileList] = useState([]);
    const [title, setTitle] = useState('');
    const [currentFile, setCurrentFile] = useState(null);
    const currentTimeToSkipRef = useRef([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [openSeasons, setOpenSeasons] = useState({});
    const [skipTimeEnabled, setSkipTimeEnabled] = useState(true);
    const { mediaId } = useParams();


    const processSeasonFiles = (seasons) => {
        return seasons.map((season) => ({
            title: season.title,
            seasonNumber: season.season_number,
            files: season.files.map(file => ({
                id: file.id,
                name: file.title,
                url: `${config.API_BASE_URL}/api/video?path=${encodeURIComponent(file.file_path)}`,
                seasonNumber: season.season_number - 1,
                episodeNumber: file.episode_number - 1,
            })),
        }));
    }

    const processMovieFiles = (collectionName, movieFiles) => {
        return {
            title: collectionName,
            files: movieFiles.parts.map(part => ({
                id: part.id,
                name: part.title,
                position: part.position - 1,
                url: part.path,
            })),
        };
    }

    const fetchMetadata = async () => {
        try {
            const item = await fetchMediaById(mediaId);
            setTitle(item.title || 'Files');
            
            if (item.type === 'series') {
                const seasons = await fetchSeriesSeasonsAndEpisodesById(mediaId);
                setFileList(processSeasonFiles(seasons));
            } else if (item.type === 'movie' && Array.isArray(item.parts)) {
                const parts = await fetchMovieItemsById(mediaId);
                setFileList(processMovieFiles(parts));
            }
        } catch (err) {
            setError(`Error fetching metadata: ${err.message}`);
        } finally {
            setLoading(false);
        }
    };

    const handleSelectFile = (seasonIndex, fileIndex) => {
        const selectedFile = fileList[seasonIndex]?.files[fileIndex];
        setCurrentFile(selectedFile);
        saveLastWatched(mediaId, selectedFile);
    };

    const handleVideoEnd = () => {
        if (fileList[currentFile.seasonNumber].files.length > currentFile.episodeNumber + 1) {
            handleSelectFile(currentFile.seasonNumber, currentFile.episodeNumber + 1);
        }
        else if (fileList.length > currentFile.seasonNumber + 1) {
            handleSelectFile(currentFile.seasonNumber + 1, 0);
        }
    };

    useEffect(() => {
        const lastFile = getLastWatched(mediaId);
        if (lastFile && fileList.length > 0) {
            if (lastFile.seasonNumber >= 0) {
                setOpenSeasons(prev => ({ ...prev, [lastFile.seasonNumber]: true }));
                setCurrentFile(lastFile);
            }
        }
    }, [fileList, mediaId, setCurrentFile, setOpenSeasons]);

    const handleToggleSkipTime = () => {
        setSkipTimeEnabled((prev) => !prev);
    };

    const handleUpdateTimeToSkip = async (updatedTimeToSkip) => {
        try {
            await updateTimeToSkip(currentFile.url, mediaId, updatedTimeToSkip);
            currentTimeToSkipRef.current = updatedTimeToSkip;
            console.log('timeToSkip updated successfully');
        } catch (error) {
            console.error(`Error updating timeToSkip: ${error.message}`);
        }
    };

    useEffect(() => {
        document.body.style.margin = '0';
        fetchMetadata();
    }, [mediaId]);

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
                    itemId={mediaId}
                    fileList={fileList}
                    currentFile={currentFile}
                    currentTitle={title}
                    openSeasons={openSeasons}
                    handleToggleSeason={handleToggleSeason}
                    handleSelectFile={handleSelectFile}
                    palette={palette}
                />
            </Box>
        </Box>
    );
};

export default Player;
