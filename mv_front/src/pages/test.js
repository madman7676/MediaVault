import React, { useState } from 'react';
import FileList from './FileList';
import PlayerControls from './PlayerControls';
import palette from '../theme/palette';

const Player = ({ metadata }) => {
    const [currentFile, setCurrentFile] = useState(null);

    const handleSelectFile = (url) => {
        setCurrentFile(url);
        localStorage.setItem('lastWatched', JSON.stringify({ itemId: metadata.id, fileUrl: url }));
    };

    return (
        <div style={{ display: 'flex', height: '100%' }}>
            <div style={{ flex: 3 }}>
                <PlayerControls
                    currentFile={currentFile}
                    onPlayerReady={(player) => console.log('Player ready:', player)}
                    handleVideoEnd={() => console.log('Video ended')}
                    currentTimeToSkip={metadata.timeToSkip || []}
                    skipTimeEnabled={true} // Example: can be managed via settings
                />
            </div>
            <div style={{ flex: 1, overflowY: 'auto' }}>
                <FileList
                    metadata={metadata}
                    currentFile={currentFile}
                    onSelectFile={handleSelectFile}
                    palette={palette}
                />
            </div>
        </div>
    );
};

export default Player;
