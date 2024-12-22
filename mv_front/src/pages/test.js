// Player.js component for displaying video and collection/season files
import 'videojs-hotkeys';
import axios from 'axios';
import videojs from 'video.js';
import 'video.js/dist/video-js.css';
import config from '../config.json';
import palette from '../theme/palette';
import { ExpandLess, ExpandMore } from '@mui/icons-material';
import React, { useState, useEffect, useRef, Fragment } from 'react';
import { Box, Typography, List, ListItem, ListItemText, Collapse } from '@mui/material';

const Player = ({ itemId = "897b7a11-268b-4eed-8ef9-4216a1ecbc7b" }) => {
    
    const playerRef = useRef(null);
    const playerInstance = useRef(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);
    const [fileList, setFileList] = useState([]);
    const [openSeasons, setOpenSeasons] = useState({});
    const [currentFile, setCurrentFile] = useState(null);
    const [isInitialized, setIsInitialized] = useState(false);
    const [currentTimeToSkip, setCurrentTimeToSkip] = useState([]);

    const initializePlayer = () => {
        if (!playerRef.current || playerInstance.current) return;

        playerInstance.current = videojs(playerRef.current, {
            controls: true,
            autoplay: false,
            preload: 'auto',
            playbackRates: [0.5, 1, 1.5, 2, 2.5],
        });

        playerInstance.current.ready(() => {
            playerInstance.current.hotkeys({
                volumeStep: 0.1,
                seekStep: 5,
                enableModifiersForNumbers: false,
            });

            // Add custom time display in control bar
            const timeControl = videojs.dom.createEl('div', {
                className: 'vjs-remaining-time vjs-time-control vjs-control',
                innerHTML: `
                    <span class="vjs-control-text" role="presentation">Current Time&nbsp;</span>
                    <span aria-hidden="true"></span>
                    <span class="vjs-remaining-time-display" role="presentation">0:00</span>`
            });

            const controlBar = playerInstance.current.controlBar;
            const volumePanel = controlBar.getChild('volumePanel');
            controlBar.el().insertBefore(timeControl, volumePanel.el().nextSibling);

            const timeDisplay = timeControl.querySelector('.vjs-remaining-time-display');

            playerInstance.current.on('timeupdate', () => {
                const currentTime = playerInstance.current.currentTime();
                const totalMinutes = Math.floor(currentTime / 60);
                const seconds = Math.floor(currentTime % 60).toString().padStart(2, '0');
                timeDisplay.innerHTML = `${totalMinutes}:${seconds}`;
            });
        });

        playerInstance.current.on('timeupdate', handleTimeUpdate);
        playerInstance.current.on('ended', handleVideoEnd);
    };

    const handleTimeUpdate = () => {
        const currentTime = playerInstance.current?.currentTime();
        if (!currentTimeToSkip || currentTimeToSkip.length === 0) return;

        const skipInterval = currentTimeToSkip.find(
            interval => currentTime >= interval.start && currentTime < interval.end
        );

        if (skipInterval) {
            playerInstance.current.currentTime(skipInterval.end);
        }
    };

    const handleVideoEnd = () => {
        const flatFileList = fileList.flatMap(season => season.files);
        const playerSrc = playerInstance.current?.currentSrc();

        const currentIndex = flatFileList.findIndex(file => decodeURIComponent(file.url) === decodeURIComponent(playerSrc || currentFile));

        if (currentIndex !== -1 && currentIndex < flatFileList.length - 1) {
            const nextFile = flatFileList[currentIndex + 1]?.url;
            if (nextFile) {
                setCurrentFile(nextFile);
                playerInstance.current.src({ src: nextFile, type: 'video/mp4' });
                playerInstance.current.load();
                playerInstance.current.play().catch(console.error);
            }
        }
    };

    const fetchMetadata = async () => {
        try {
            const response = await axios.get(`${config.API_BASE_URL}/api/metadata/item/${itemId}`);
            const { item, status } = response.data;

            if (status === 'success') {
                const files = item.type === 'series'
                    ? item.seasons.map((season, seasonIndex) => ({
                          seasonTitle: `Сезон ${seasonIndex + 1}`,
                          files: season.files.map(file => ({
                              url: `${config.API_BASE_URL}/api/video?path=${encodeURIComponent(season.path + '/' + file.name)}`,
                              name: file.name,
                              timeToSkip: file.timeToSkip || [],
                          })),
                      }))
                    : [{
                          seasonTitle: 'Collection',
                          files: item.parts.map(part => ({
                              url: `${config.API_BASE_URL}/api/video?path=${encodeURIComponent(part.path)}`,
                              name: part.title,
                              timeToSkip: part.timeToSkip || [],
                          })),
                      }];
                setFileList(files);
            } else {
                setError('Failed to load item metadata.');
            }
        } catch {
            setError('Error fetching metadata from server.');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        document.body.style.margin = '0';
        fetchMetadata();
    }, [itemId]);

    useEffect(() => {
        if (isInitialized) initializePlayer();

        return () => {
            if (playerInstance.current) {
                playerInstance.current.dispose();
                playerInstance.current = null;
            }
        };
    }, [fileList, isInitialized]);

    useEffect(() => {
        const selectedFileMetadata = fileList
            .flatMap(season => season.files)
            .find(file => file.url === currentFile);

        setCurrentTimeToSkip(selectedFileMetadata?.timeToSkip || []);

        if (playerInstance.current && currentFile) {
            playerInstance.current.src({ src: currentFile, type: 'video/mp4' });
            playerInstance.current.load();
            playerInstance.current.play().catch(console.error);
        }
    }, [fileList, currentFile]);

    const handleToggleSeason = seasonIndex => {
        setOpenSeasons(prev => ({
            ...prev,
            [seasonIndex]: !prev[seasonIndex],
        }));
    };

    const handlePlay = () => {
        if (playerInstance.current) {
            playerInstance.current.play().catch(console.error);
        }
        setIsInitialized(true);
    };

    const handleSelectFile = url => {
        setCurrentFile(url);
        handlePlay();
    };

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
                {currentFile ? (
                    <div data-vjs-player style={{ width: '100%', height: '100%' }}>
                        <video ref={playerRef} className="video-js" />
                    </div>
                ) : (
                    <Typography variant="h6" sx={{ color: palette.text.lightPrimary }}>
                        No video selected
                    </Typography>
                )}
            </Box>

            <Box
                sx={{
                    flex: 1,
                    overflow: 'hidden',
                    borderLeft: 'none',
                    padding: 2,
                    backgroundColor: palette.background.card,
                }}
            >
                <Typography variant="h6" sx={{ marginBottom: 2, color: palette.text.lightPrimary }}>
                    Files in Collection
                </Typography>
                {fileList.length > 0 ? (
                    <List>
                        {fileList.map((season, seasonIndex) => (
                            <Fragment key={seasonIndex}>
                                <ListItem disablePadding sx={{ cursor: 'pointer' }} onClick={() => handleToggleSeason(seasonIndex)}>
                                    <ListItemText primary={season.seasonTitle} sx={{ color: palette.text.lightPrimary }} />
                                    {openSeasons[seasonIndex] ? <ExpandLess /> : <ExpandMore />}
                                </ListItem>
                                <Collapse in={openSeasons[seasonIndex]} timeout="auto" unmountOnExit>
                                    {season.files.map((file, fileIndex) => (
                                        <ListItem
                                            key={fileIndex}
                                            button
                                            onClick={() => { handleSelectFile(file.url);}}
                                            selected={currentFile === file.url}
                                            sx={{
                                                cursor: 'pointer',
                                                color: currentFile === file.url ? palette.primary : palette.text.lightPrimary,
                                                backgroundColor: currentFile === file.url ? palette.background.paper : 'transparent',
                                                '&:hover': { backgroundColor: palette.secondary, color: palette.text.lightSecondary },
                                                '&:active': { backgroundColor: palette.primary, opacity: 0.8 },
                                            }}
                                        >
                                            <ListItemText primary={file.name} />
                                        </ListItem>
                                    ))}
                                </Collapse>
                            </Fragment>
                        ))}
                    </List>
                ) : (
                    <Typography variant="body1" sx={{ color: palette.text.lightSecondary }}>
                        No files available
                    </Typography>
                )}
            </Box>
        </Box>
    );
};

export default Player;
