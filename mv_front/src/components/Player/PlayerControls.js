// PlayerControls.js: Component for managing the video.js player
import React, { useEffect, useRef, useState } from 'react';
import ReactDOM from 'react-dom/client';
import videojs from 'video.js';
import 'video.js/dist/video-js.css';
import 'videojs-hotkeys';
import SettingsMenu from './SettingsMenu';
import TimeToSkipSettingsMenu from './TimeToSkipSettingsMenu';
import { fetchTimeToSkip } from '../../api/metadataAPI';
import { getAudioTracks } from '../../api/videoAPI';
import AudioTracksSubmenu from './AudioTracksSubmenu';

const PlayerControls = ({
    currentFile,
    currentPath,
    currentName,
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
    const currentPathRef = useRef(null);
    const currentNameRef = useRef(null);
    const [showTimeToSkipMenu, setShowTimeToSkipMenu] = useState(false);
    const [showAudioSubmenu, setShowAudioSubmenu] = useState(false);
    const [audioTracks, setAudioTracks] = useState([]);
    const [currentAudioTrack, setCurrentAudioTrack] = useState(0);

    const handleOptionSelect = (option, menu) => {
        if (option === 'audioTracks') {
            // setShowAudioSubmenu (!showAudioSubmenu);

            const fullPath = currentPathRef.current && currentNameRef.current ? 
            `${currentPathRef.current}\\${currentNameRef.current}` : null;
            console.log('Current file:', fullPath);
            if (!fullPath) {
                console.error('Cannot get full file path');
                return;
            }
            getAudioTracks(fullPath)
            .then(tracks => {
                const tracksInfo = tracks.map((track, index) => ({
                    index,
                    label: track.title || `Audio ${index + 1}`,
                    language: track.language,
                    enabled: index === currentAudioTrack
                }));
                setAudioTracks(tracksInfo);
            })
            .catch(error => {
                console.error('Failed to load audio tracks:', error);
                setAudioTracks([]);
            });
            return;
        }
        if (option === 'openTimeToSkipMenu') {
            setShowTimeToSkipMenu(true);
        }
        menu.style.display = 'none';
    };

    const handleTrackSelect = (index) => {
        console.log('Changing audio track to:', index);
        setCurrentAudioTrack(index);
        
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
        if (!progressBar || !playerInstance.current || !playerInstance.current.duration()) return;

        // Очистити попередні елементи
        const existingSkips = progressBar.querySelectorAll('.time-skip-highlight');
        existingSkips.forEach((element) => element.remove());

        const videoDuration = playerInstance.current.duration();

        // Додати нові
        intervals.forEach(({ start, end }) => {
            if (start >= 0 && end <= videoDuration) {
                const skipElement = document.createElement('div');
                skipElement.className = 'time-skip-highlight';
                skipElement.style.position = 'absolute';
                skipElement.style.height = '100%';
                skipElement.style.backgroundColor = 'rgba(0, 0, 255, 0.5)';
                skipElement.style.left = `${(start / videoDuration) * 100}%`;
                skipElement.style.width = `${((end - start) / videoDuration) * 100}%`;
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
            const root = ReactDOM.createRoot(menu);
            root.render(
                <SettingsMenu
                    ref={settingsMenuRef}
                    buttonRef={settingsButtonRef}
                    onOptionSelect={(option) => handleOptionSelect(option, menu)}
                />
            );

            menu.style.display = 'none';
            menu.style.position = 'absolute';

            settingsButton.addEventListener('click', (event) => {
                event.stopPropagation();
                const isMenuOpen = menu.style.display === 'block';
                menu.style.display = isMenuOpen ? 'none' : 'block';
                if (settingsMenuRef.current) {
                    settingsMenuRef.current.calculateMenuPosition(); // Виклик методу
                }
            });

            document.addEventListener('click', () => {
                menu.style.display = 'none';
            });

            settingsContainer.appendChild(settingsButton);
            settingsContainer.appendChild(menu);

            const fullscreenControl = controlBar.el().querySelector('.vjs-fullscreen-control');
            if (fullscreenControl) {
                controlBar.el().insertBefore(settingsContainer, fullscreenControl);
            }
        }

        playerInstance.current.on('ended', handleVideoEnd);
    };

    useEffect(() => {
        if (!playerRef.current) return;

        initializePlayer();

        return () => {
            if (playerInstance.current && playerInstance.current.readyState() !== 0) {
                playerInstance.current.dispose();
                playerInstance.current = null;
            }
        };
    }, []);

    useEffect(() => {
        if (playerInstance.current && currentFile) {
            playerInstance.current.src({ src: currentFile, type: 'video/mp4' });
            playerInstance.current.load();

            playerInstance.current.play().catch(console.error);
        }
    }, [currentFile]);

    useEffect(() => {
        const loadTimeToSkip = async () => {
            try {
                const timeToSkip = await fetchTimeToSkip(currentPath, currentName);
                console.log('Fetched timeToSkip:', timeToSkip);
                currentTimeToSkip.current = timeToSkip;
                currentPathRef.current = currentPath;
                currentNameRef.current = currentName;
                renderTimeSkips(timeToSkip); // Рендерити пропуски
            } catch (error) {
                console.error(`Error fetching timeToSkip: ${error.message}`);
            }
        };

        if (currentPath && currentName) {
            loadTimeToSkip();
        }
    }, [currentPath, currentName]);

    useEffect(() => {
        if (playerInstance.current) {
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
        }
    }, [currentTimeToSkip, skipTimeEnabled]);

    useEffect(() => {
        if (!playerInstance.current) return;
    
        const onEnded = () => {
            console.log('Video ended');
            handleVideoEnd();
        };
    
        playerInstance.current.on('ended', onEnded);
    
        return () => {
            if (playerInstance.current) {
                console.log('Removing ended listener');
                playerInstance.current.off('ended', onEnded);
            }
        };
    }, [handleVideoEnd]);    

    useEffect(() => {
        if (playerInstance.current) {
            const handleError = (error) => {
                console.error('Audio track error:', error);
            };
    
            const handleTrackChange = () => {
                const tracks = playerInstance.current.audioTracks();
                if (tracks) {
                    const currentIndex = Array.from(tracks).findIndex(track => track.enabled);
                    setCurrentAudioTrack(currentIndex);
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
        }
    }, []);

    useEffect(() => {
        // Add styles after player initialization
        if (playerInstance.current) {
            const style = document.createElement('style');
            style.textContent = `
                .video-js:focus { outline: none !important; }
                .video-js *:focus { outline: none !important; }
                .vjs-control:focus { outline: none !important; }
            `;
            document.head.appendChild(style);

            return () => {
                document.head.removeChild(style);
            };
        }
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
                        renderTimeSkips(updatedIntervals); // Рендерити пропуски
                    }}
                    onClose={handleCloseTimeToSkipMenu}
                    currentPath={currentPathRef.current}
                    currentName={currentNameRef.current}
                />
            )}
            {showAudioSubmenu && (
                <AudioTracksSubmenu
                    tracks={audioTracks}
                    currentTrack={currentAudioTrack}
                    onTrackSelect={handleTrackSelect}
                />
            )}
        </div>
    );
};

export default PlayerControls;
