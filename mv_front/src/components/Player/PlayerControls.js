// PlayerControls.js: Component for managing the video.js player
import React, { useEffect, useRef } from 'react';
import videojs from 'video.js';
import 'video.js/dist/video-js.css';

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

        // Власні обробники хоткеїв
        playerInstance.current.on('keydown', function (event) {
            switch (event.key) {
                case ' ':
                    // Пробіл — відтворити / поставити на паузу
                    playerInstance.current.paused() ? playerInstance.current.play() : playerInstance.current.pause();
                    break;
                case 'ArrowRight':
                    // Стрілка вправо — перемотати на 10 секунд
                    playerInstance.current.currentTime(playerInstance.current.currentTime() + 5);
                    break;
                case 'ArrowLeft':
                    // Стрілка вліво — перемотати на 10 секунд назад
                    playerInstance.current.currentTime(playerInstance.current.currentTime() - 5);
                    break;
                case 'ArrowUp':
                    // Стрілка вгору — збільшити гучність
                    let volume = playerInstance.current.volume();
                    if (volume < 1) playerInstance.current.volume(volume + 0.1);
                    break;
                case 'ArrowDown':
                    // Стрілка вниз — зменшити гучність
                    volume = playerInstance.current.volume();
                    if (volume > 0) playerInstance.current.volume(volume - 0.1);
                    break;
                case 'f':
                    // 'f' — на повний екран
                    if (playerInstance.current.isFullscreen()) {
                        playerInstance.current.exitFullscreen();
                    } else {
                        playerInstance.current.requestFullscreen();
                    }
                    break;
                default:
                    break;
            }
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
            settingsButton.style.fontSize = '16px'; // Розмір іконки
            settingsButton.style.width = '40px'; // Розмір кнопки
            settingsButton.style.height = '30px'; // Розмір кнопки
            settingsButton.style.display = 'inline-flex';
            settingsButton.style.justifyContent = 'center';
            settingsButton.style.alignItems = 'center';
        
            controlBar.el().appendChild(settingsButton);

            // Переміщаємо кнопку перед `fullscreenControl`
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

            // Стилі для прихованого меню
            menu.style.display = 'none';
            menu.style.position = 'absolute';
            menu.style.backgroundColor = '#000';
            menu.style.color = '#fff';
            menu.style.padding = '10px';
            menu.style.borderRadius = '4px';

            settingsButton.addEventListener('click', (event) => {
                event.stopPropagation(); // Запобігає закриттю при кліку на кнопку
                const isMenuOpen = menu.style.display === 'block';
                menu.style.display = isMenuOpen ? 'none' : 'block';
            
                // Розташування меню під кнопкою
                const rect = settingsButton.getBoundingClientRect();
                menu.style.top = `${rect.bottom + window.scrollY}px`;
                menu.style.left = `${rect.left + window.scrollX}px`;
            });

            document.addEventListener('click', () => {
                menu.style.display = 'none';
            });

            menu.addEventListener('click', (event) => {
                if (event.target.classList.contains('vjs-menu-item')) {
                    console.log(`Selected: ${event.target.textContent}`);
                    menu.style.display = 'none'; // Закрити меню після вибору
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
