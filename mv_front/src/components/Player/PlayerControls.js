// PlayerControls.js: Component for managing the video.js player
import React, { useEffect, useRef } from 'react';
import videojs from 'video.js';
import 'video.js/dist/video-js.css';
import 'videojs-hotkeys';

const PlayerControls = ({
    currentFile,
    onPlayerReady,
    handleVideoEnd,
    currentTimeToSkip,
    skipTimeEnabled
}) => {
    const playerRef = useRef(null);
    const playerInstance = useRef(null);

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
        
            controlBar.el().appendChild(settingsButton);

            const fullscreenControl = controlBar.el().querySelector('.vjs-fullscreen-control');
            if (fullscreenControl) {
                controlBar.el().insertBefore(settingsButton, fullscreenControl);
            }

            const menu = videojs.dom.createEl('div', {
                className: 'vjs-settings-menu',
                innerHTML: `
                    <ul class="vjs-menu-content">
                        <li class="vjs-menu-item">Option 1</li>
                        <li class="vjs-menu-item">Option 2</li>
                        <li class="vjs-menu-item">Option 3</li>
                    </ul>
                `
            });

            menu.style.display = 'none';
            menu.style.position = 'absolute';
            menu.style.backgroundColor = '#000';
            menu.style.color = '#fff';
            menu.style.padding = '10px';
            menu.style.borderRadius = '4px';

            settingsButton.addEventListener('click', (event) => {
                event.stopPropagation();
                const isMenuOpen = menu.style.display === 'block';
                menu.style.display = isMenuOpen ? 'none' : 'block';

                const rect = settingsButton.getBoundingClientRect();
                const menuWidth = 200; // Assume menu width for calculations
                const menuHeight = 120; // Assume menu height for calculations

                let top = rect.bottom + window.scrollY;
                let left = rect.left + window.scrollX;

                // Ensure menu stays within viewport
                if (top + menuHeight > window.innerHeight + window.scrollY) {
                    top = rect.top + window.scrollY - menuHeight;
                }

                if (left + menuWidth > window.innerWidth + window.scrollX) {
                    left = window.innerWidth + window.scrollX - menuWidth;
                }

                menu.style.top = `${top}px`;
                menu.style.left = `${left}px`;
            });

            document.addEventListener('click', () => {
                menu.style.display = 'none';
            });

            menu.addEventListener('click', (event) => {
                if (event.target.classList.contains('vjs-menu-item')) {
                    console.log(`Selected: ${event.target.textContent}`);
                    menu.style.display = 'none';
                }
            });            

            controlBar.el().appendChild(menu);
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
        if (playerInstance.current) {
            playerInstance.current.on('ended', () => {
                handleVideoEnd();
            });
        }
    
        return () => {
            if (playerInstance.current) {
                playerInstance.current.off('ended');
            }
        };
    }, [handleVideoEnd]);

    useEffect(() => {
        if (playerInstance.current) {
            const handleTimeUpdate = () => {
                const currentTime = playerInstance.current.currentTime();
                if (!currentTimeToSkip || currentTimeToSkip.length === 0 || !skipTimeEnabled) return;

                const skipInterval = currentTimeToSkip.find(
                    interval => currentTime >= interval.start && currentTime < interval.end
                );

                if (skipInterval) {
                    console.log(`Skipping to ${skipInterval.end}`);
                    playerInstance.current.currentTime(skipInterval.end);
                }
            };

            playerInstance.current.on('timeupdate', handleTimeUpdate);

            return () => {
                if (playerInstance.current) {
                    playerInstance.current.off('timeupdate', handleTimeUpdate);
                }
            };
        }
    }, [currentTimeToSkip, skipTimeEnabled]);

    return (
        <div data-vjs-player style={{ width: '100%', height: '100%' }}>
            <video ref={playerRef} className="video-js" />
        </div>
    );
};

export default PlayerControls;
