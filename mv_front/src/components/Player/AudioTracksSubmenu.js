import React, { useRef, useEffect } from 'react';

const AudioTracksSubmenu = ({ tracks, onTrackSelect, currentTrack }) => {
    const menuRef = useRef(null);

    const menuStyles = {
        position: 'absolute',
        backgroundColor: '#000',
        color: '#fff',
        padding: '10px 5px',
        borderRadius: '4px',
        width: 'fit-content',
        right: '5.3%',
        bottom: '40px',
        top: '87%',
        marginRight: '5px'
    };

    const listStyles = {
        padding: 0,
        listStyleType: 'none',
        margin: 0,
        textAlign: 'left',
    };

    const listItemStyles = {
        cursor: 'pointer',
        padding: '5px 10px',
        whiteSpace: 'nowrap',
    };

    return (
        <div ref={menuRef} style={menuStyles}>
            <ul style={listStyles}>
            {tracks.map((track) => (
                <li
                    key={track.index}
                    style={{
                        ...listItemStyles,
                        backgroundColor: currentTrack === track.index ? '#555' : 'transparent'
                    }}
                    onMouseEnter={(e) => e.target.style.backgroundColor = '#555'}
                    onMouseLeave={(e) => e.target.style.backgroundColor = 
                        currentTrack === track.index ? '#555' : 'transparent'}
                    onClick={() => onTrackSelect(track.index)}
                >
                    {track.label}
                    {track.language && ` (${track.language})`}
                </li>
            ))}
            </ul>
        </div>
    );
};

export default AudioTracksSubmenu;