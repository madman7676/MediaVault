// Player.js component for displaying video and collection/season files
import 'videojs-hotkeys';
import axios from 'axios';
import config from '../config.json';
import palette from '../theme/palette';
import FileList from '../components/FileList';
import PlayerControls from '../components/Player/PlayerControls';
import { Settings, CheckBox, CheckBoxOutlineBlank } from '@mui/icons-material';
import React, { useState, useEffect, useRef } from 'react';
import { Box, Typography, Menu, MenuItem, Checkbox, IconButton } from '@mui/material';
import { useParams } from 'react-router-dom';

const Player = () => {
    const [fileList, setFileList] = useState([]);
    const [title, setTitle] = useState('');
    const [currentFile, setCurrentFile] = useState(null);
    const currentTimeToSkipRef = useRef([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [openSeasons, setOpenSeasons] = useState({});
    const [settingsAnchorEl, setSettingsAnchorEl] = useState(null);
    const [skipTimeEnabled, setSkipTimeEnabled] = useState(true);
    const { itemId } = useParams();

    const handleOpenSettingsMenu = (event) => {
        setSettingsAnchorEl(event.currentTarget);
    };

    const handleCloseSettingsMenu = () => {
        setSettingsAnchorEl(null);
    };

    const handleToggleSkipTime = () => {
        setSkipTimeEnabled((prev) => !prev);
    };

    const handleEditSkipTime = () => {
        console.log("Edit skip time settings (to be implemented)");
    };

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
                currentTimeToSkipRef.current = nextFile.timeToSkip || [];

                setCurrentFile(nextFile.url);
                localStorage.setItem('lastWatched', JSON.stringify({ itemId, fileUrl: nextFile.url }));
            }
        }
    };

    const fetchMetadata = async () => {
        try {
            const response = await axios.get(`${config.API_BASE_URL}/api/metadata/item/${itemId}`);
            const { item, status } = response.data;

            if (status === 'success') {
                setTitle(item.title || 'Files');
                setFileList(processFiles(item));
            } else {
                setError('Failed to load item metadata.');
            }
        } catch (err) {
            setError(`Error fetching metadata: ${err.message}`);
        } finally {
            setLoading(false);
        }
    };

    const handleSelectFile = (url) => {
        const selectedFileMetadata = fileList
            .flatMap(season => season.files)
            .find(file => file.url === url);

        currentTimeToSkipRef.current = selectedFileMetadata?.timeToSkip || [];
        setCurrentFile(url);
        localStorage.setItem('lastWatched', JSON.stringify({ itemId, fileUrl: url }));
    };

    useEffect(() => {
        document.body.style.margin = '0';
        fetchMetadata();
    }, [itemId]);

    useEffect(() => {
        const lastWatched = JSON.parse(localStorage.getItem('lastWatched'));
        if (lastWatched?.itemId === itemId && fileList.length > 0) {
            const flatFileList = fileList.flatMap(season => season.files);
            const lastFile = flatFileList.find(file => file.url === lastWatched.fileUrl);
            if (lastFile) {
                const seasonIndex = fileList.findIndex(season =>
                    season.files.some(file => file.url === lastWatched.fileUrl)
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

    if (loading) return <Typography>Loading...</Typography>;
    if (error) return <Typography color="error">{error}</Typography>;

    return (
        <>
            {/* <Menu
                anchorEl={settingsAnchorEl}
                open={Boolean(settingsAnchorEl)}
                onClose={handleCloseSettingsMenu}
            >
                <MenuItem>
                    <Checkbox
                        checked={skipTimeEnabled}
                        onChange={handleToggleSkipTime}
                        icon={<CheckBoxOutlineBlank />}
                        checkedIcon={<CheckBox />}
                    />
                    <Typography sx={{ flex: 1 }}>Час для пропуску</Typography>
                    <IconButton onClick={handleEditSkipTime}>
                        <Settings />
                    </IconButton>
                </MenuItem>
            </Menu> */}
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
                        currentFile={currentFile}
                        currentTimeToSkip={currentTimeToSkipRef.current}
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
                        fileList={fileList}
                        currentFile={currentFile}
                        openSeasons={openSeasons}
                        handleToggleSeason={handleToggleSeason}
                        handleSelectFile={handleSelectFile}
                        palette={palette}
                        lastWatched={JSON.parse(localStorage.getItem('lastWatched'))?.fileUrl}
                    />
                </Box>
            </Box>
        </>
    );
};

export default Player;
