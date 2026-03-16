// PlayerControls.js: Component for managing the video.js player
import React, { useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import videojs from 'video.js';
import 'video.js/dist/video-js.css';
import 'videojs-hotkeys';
import SettingsMenu from './SettingsMenu';
import TimeToSkipSettingsMenu from './TimeToSkipSettingsMenu';
import { fetchDefaultBookmarks } from '../../api/bookmarksAPI';
import { formatTime, parseTimeInput } from '../../utils/timeUtils';


const PlayerControls = ({
    currentFile,
    onPlayerReady,
    handleVideoEnd,
    skipTimeEnabled
}) => {
    const playerRef = useRef(null);
    const playerInstance = useRef(null);
    const settingsButtonRef = useRef(null);
    const settingsMenuRef = useRef(null);
    const timeToSkipMenuRef = useRef(null);
    const currentTimeToSkip = useRef([]);
    const [showTimeToSkipMenu, setShowTimeToSkipMenu] = useState(false);
    const fetchAbortControllerRef = useRef(null);
    const globalClickHandlerRef = useRef(null);
    const stylesRef = useRef(null);

    const [pendingTemplate, setPendingTemplate] = useState(null);


    const handleOptionSelect = (option, menu) => {
        if (option === 'openTimeToSkipMenu') {
            setShowTimeToSkipMenu(true);
        } else if (option.includes('+')) { // ToDo - refactor this to use a custom hook for creating skip sets based on templates
            // Handle fast skip options
            const videoElement = document.querySelector('.video-js video');
            const currentTime = videoElement ? Math.floor(videoElement.currentTime) : 0;
            const duration = videoElement ? Math.floor(videoElement.duration) : 0;
            const parsedCurrentTime = parseTimeInput(formatTime(currentTime));
            const parsedDuration = parseTimeInput(formatTime(duration));

            const optionsMap = {
                '0+1:30': [0, 90],
                '0+current': [0, parsedCurrentTime],
                'current+1:30': [parsedCurrentTime, parsedCurrentTime + 90],
                'current+end': [parsedCurrentTime, parsedDuration]
            };

            const [startTime, endTime] = optionsMap[option] || [0, 0];

            if (startTime < endTime) {
                setPendingTemplate({ start: startTime, end: endTime, timeSpamp: Date.now() });
                setShowTimeToSkipMenu(true);
            } else {
                console.error('Invalid skip times');
            }
        }
        menu.style.display = 'none';
    };

    const handleTrackSelect = (index) => {
        console.log('Changing audio track to:', index);
        
        if (playerInstance.current) {
            const tracks = playerInstance.current.audioTracks();
            console.log('Available tracks:', tracks);
            
            if (tracks && tracks.length > 0) {
                tracks.forEach((track, i) => {
                    track.enabled = (i === index);
                });
                console.log('Track changed successfully');
            } else {
                console.error('No audio tracks available');
            }
        }
    };
    
    const handleCloseTimeToSkipMenu = () => {
        setShowTimeToSkipMenu(false);
        if (playerRef.current) {
            playerRef.current.focus();
        }
    };

    const renderTimeSkips = (intervals) => {
        const progressBar = document.querySelector('.vjs-progress-holder');
        if (!progressBar || !playerInstance.current) return;

        const duration = playerInstance.current.duration();
        if (!duration || !isFinite(duration)) return;

        // Очистити попередні елементи
        const existingSkips = progressBar.querySelectorAll('.time-skip-highlight');
        existingSkips.forEach((element) => element.remove());

        // Додати нові
        intervals.forEach(({ start, end }) => {
            if (start >= 0 && end <= duration) {
                const skipElement = document.createElement('div');
                skipElement.className = 'time-skip-highlight';
                skipElement.style.position = 'absolute';
                skipElement.style.height = '100%';
                skipElement.style.backgroundColor = 'rgba(0, 0, 255, 0.5)';
                skipElement.style.left = `${(start / duration) * 100}%`;
                skipElement.style.width = `${((end - start) / duration) * 100}%`;
                progressBar.appendChild(skipElement);
            }
        });
    };

    const initializePlayer = () => {
        if (playerInstance.current) return; // Prevent re-initialization

        playerInstance.current = videojs(playerRef.current, {
            controls: true,
            autoplay: false,
            preload: 'auto',
            playbackRates: [0.5, 1, 1.5, 2, 2.5],
            controlBar: {
                children: [
                    'playToggle',
                    'volumePanel',
                    'currentTimeDisplay',
                    'timeDivider',
                    'durationDisplay',
                    'progressControl',
                    'playbackRateMenuButton',
                    'fullscreenToggle'
                ]
            }
        }, function() {
            this.on('ready', () => {
                const progressElement = this.el().querySelector('.vjs-play-progress.vjs-slider-bar');
                if (progressElement) {
                    const timeTooltip = progressElement.querySelector('.vjs-time-tooltip');
                    if (timeTooltip) {
                        timeTooltip.style.display = 'none';
                    }
                }
            });
        });

        playerInstance.current.hotkeys({
            volumeStep: 0.1,
            seekStep: 5,
            enableModifiersForNumbers: false
        });

        const controlBar = playerInstance.current.controlBar;
        ['currentTimeDisplay', 'durationDisplay', 'timeDivider'].forEach((child) => {
            const component = controlBar.getChild(child);
            if (component) {
                const el = component.el();
                el.style.display = 'flex';
                el.style.visibility = 'visible';
                el.style.opacity = '1';
                el.style.padding = '0 5px';
                el.style.minWidth = '0';
            }
        });

        if (!controlBar.el().querySelector('.vjs-settings-button')) {
            const settingsContainer = videojs.dom.createEl('div', {
                className: 'vjs-settings-container',
                style: 'position: relative; display: inline-block;'
            });

            const settingsButton = videojs.dom.createEl('button', {
                className: 'vjs-settings-button vjs-control vjs-button vjs-icon-cog',
                title: 'Settings',
                ariaLabel: 'Settings',
            });
            settingsButton.style.fontSize = '16px';
            settingsButton.style.width = '40px';
            settingsButton.style.height = '30px';
            settingsButton.style.display = 'inline-flex';
            settingsButton.style.justifyContent = 'center';
            settingsButton.style.alignItems = 'center';

            settingsButtonRef.current = settingsButton;

            const menu = document.createElement('div');
            menu.id = 'settingsMenu';
            const root = createRoot(menu);
            root.render(
                <SettingsMenu
                    ref={settingsMenuRef}
                    buttonRef={settingsButtonRef}
                    onOptionSelect={(option) => handleOptionSelect(option, menu)}
                />
            );

            menu.style.display = 'none';
            menu.style.position = 'absolute';
            menu.style.top = '0';
            menu.style.left = '0';
            menu.style.width = '100%';
            menu.style.height = '100%';
            menu.style.pointerEvents = 'none';

            const handleSettingsClick = (event) => {
                event.stopPropagation();
                const isMenuOpen = menu.style.display === 'block';
                menu.style.display = isMenuOpen ? 'none' : 'block';
                if (settingsMenuRef.current) {
                    settingsMenuRef.current.calculateMenuPosition?.();
                }
            };

            const handleGlobalClick = (event) => {
                if (!settingsContainer.contains(event.target)) {
                    menu.style.display = 'none';
                }
            };

            settingsButton.addEventListener('click', handleSettingsClick);
            globalClickHandlerRef.current = handleGlobalClick;
            document.addEventListener('click', handleGlobalClick);

            settingsContainer.appendChild(settingsButton);
            playerInstance.current.el().appendChild(menu);

            const fullscreenControl = controlBar.el().querySelector('.vjs-fullscreen-control');
            if (fullscreenControl) {
                controlBar.el().insertBefore(settingsContainer, fullscreenControl);
            }
        }
    };

    // Додати стилі один раз
    useEffect(() => {
        const style = document.createElement('style');
        style.textContent = `
            .video-js:focus { outline: none !important; }
            .video-js *:focus { outline: none !important; }
            .vjs-control:focus { outline: none !important; }
        `;
        document.head.appendChild(style);
        stylesRef.current = style;

        return () => {
            if (stylesRef.current && document.head.contains(stylesRef.current)) {
                document.head.removeChild(stylesRef.current);
            }
        };
    }, []);

    // Ініціалізація плеєра
    useEffect(() => {
        if (!playerRef.current) return;

        initializePlayer();

        return () => {
            // Видалити глобальний обробник
            if (globalClickHandlerRef.current) {
                document.removeEventListener('click', globalClickHandlerRef.current);
                globalClickHandlerRef.current = null;
            }

            if (playerInstance.current && playerInstance.current.readyState() !== 0) {
                playerInstance.current.dispose();
                playerInstance.current = null;
            }
        };
    }, []);

    // Завантажити відео
    useEffect(() => {
        if (!playerInstance.current || !currentFile?.url) return;

        const p = playerInstance.current;
        p.src({ src: currentFile.url, type: 'video/mp4' });

        p.play().catch((e) => {
            if (e.name !== 'AbortError') return;
            console.error(e);
        });
    }, [currentFile?.url]);

    // Завантажити пропуски часу
    useEffect(() => {
        const episodeId = currentFile?.id;

        // Одразу очистити старі пропуски при зміні серії
        currentTimeToSkip.current = [];
        renderTimeSkips([]);
        
        // Скасувати попередній запит
        if (fetchAbortControllerRef.current) {
            fetchAbortControllerRef.current.abort();
        }
        
        const loadTimeToSkip = async (id) => {
            if (!id) {
                currentTimeToSkip.current = [];
                renderTimeSkips([]);
                return;
            }

            try {
                fetchAbortControllerRef.current = new AbortController();
                const rawTimeToSkip = await fetchDefaultBookmarks(id);
                
                const timeToSkip = rawTimeToSkip.map(({ start_time_ms, end_time_ms, id }) => ({
                    start: start_time_ms,
                    end: end_time_ms,
                    id: id
                }));
                currentTimeToSkip.current = timeToSkip;
                renderTimeSkips(currentTimeToSkip.current);
            } catch (error) {
                if (error.name !== 'AbortError') {
                    console.error(`Error fetching timeToSkip: ${error.message}`);
                    currentTimeToSkip.current = [];
                    renderTimeSkips([]);
                }
            }
        };
        
        loadTimeToSkip(episodeId);

        return () => {
            if (fetchAbortControllerRef.current) {
                fetchAbortControllerRef.current.abort();
            }
        };
    }, [currentFile?.id]);

    // Обробка часу відтворення і пропусків
    useEffect(() => {
        if (!playerInstance.current) return;

        const handleTimeUpdate = () => {
            const currentTime = playerInstance.current.currentTime();
            if (!currentTimeToSkip.current || currentTimeToSkip.current.length === 0 || !skipTimeEnabled) return;

            const skipInterval = currentTimeToSkip.current.find(
                interval => currentTime >= interval.start && currentTime < interval.end
            );
            if (skipInterval) {
                console.log(`Skipping to ${skipInterval.end}`);
                playerInstance.current.currentTime(skipInterval.end);
            }
        };

        const handleLoadedMetadata = () => {
            renderTimeSkips(currentTimeToSkip.current);
        };

        playerInstance.current.on('timeupdate', handleTimeUpdate);
        playerInstance.current.on('loadedmetadata', handleLoadedMetadata);

        return () => {
            if (playerInstance.current) {
                playerInstance.current.off('timeupdate', handleTimeUpdate);
                playerInstance.current.off('loadedmetadata', handleLoadedMetadata);
            }
        };
    }, [skipTimeEnabled]);

    // Обробник завершення відео
    useEffect(() => {
        if (!playerInstance.current) return;

        const onEnded = () => {
            console.log('Video ended');
            handleVideoEnd();
        };

        playerInstance.current.on('ended', onEnded);

        return () => {
            if (playerInstance.current) {
                playerInstance.current.off('ended', onEnded);
            }
        };
    }, [handleVideoEnd]);

    // Обробники аудіотреків
    useEffect(() => {
        if (!playerInstance.current) return;

        const handleError = (error) => {
            console.error('Audio track error:', error);
        };

        const handleTrackChange = () => {
            const tracks = playerInstance.current.audioTracks();
            if (tracks) {
                Array.from(tracks).findIndex(track => track.enabled);
            }
        };

        playerInstance.current.on('error', handleError);
        playerInstance.current.on('audiotrackchange', handleTrackChange);

        return () => {
            if (playerInstance.current) {
                playerInstance.current.off('error', handleError);
                playerInstance.current.off('audiotrackchange', handleTrackChange);
            }
        };
    }, []);

    return (
        <div data-vjs-player style={{ width: '100%', height: '100%' }}>
            <video ref={playerRef} className="video-js" />
            {showTimeToSkipMenu && (
                <TimeToSkipSettingsMenu
                    intervals={currentTimeToSkip.current}
                    onIntervalsChange={(updatedIntervals) => {
                        console.log('Updated intervals:', updatedIntervals);
                        currentTimeToSkip.current = updatedIntervals;
                        renderTimeSkips(updatedIntervals);
                    }}
                    onClose={handleCloseTimeToSkipMenu}
                    currentEpisodeId={currentFile?.id}
                    pendingTemplate={pendingTemplate}
                />
            )}
        </div>
    );
};

export default PlayerControls;