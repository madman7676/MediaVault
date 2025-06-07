import React, { useRef, useState, useImperativeHandle, forwardRef } from 'react';

const SettingsMenu = forwardRef(({ onOptionSelect, buttonRef }, ref) => {
    const menuRef = useRef(null);
    const [menuStyles, setMenuStyles] = useState({
        position: 'absolute',
        backgroundColor: '#000',
        color: '#fff',
        padding: '10px 5px',
        borderRadius: '4px',
        display: 'none',
        width: 'fit-content',
    });

    const calculateMenuPosition = () => {
        if (buttonRef.current && menuRef.current) {
            const buttonRect = buttonRef.current.getBoundingClientRect();
            const menuWidth = menuRef.current.offsetWidth;

            setMenuStyles((prevStyles) => ({
                ...prevStyles,
                bottom: `${window.innerHeight - buttonRect.top}px`,
                left: `0px`,
                display: 'block',
            }));
        }
    };

    // Expose calculateMenuPosition to the parent via ref
    useImperativeHandle(ref, () => ({
        calculateMenuPosition,
    }));

    const listStyles = {
        padding: 0,
        listStyleType: 'none',
        margin: 0,
        textAlign: 'center',
    };

    const listItemStyles = {
        cursor: 'pointer',
        padding: '5px 10px',
        textAlign: 'center',
        whiteSpace: 'nowrap',
    };

    const listItemHoverStyles = {
        backgroundColor: '#555',
    };

    return (
        <div
            className="vjs-settings-menu"
            ref={menuRef}
            style={menuStyles}
        >
            <ul className="vjs-menu-content" style={listStyles}>
                <li
                    className="vjs-menu-item"
                    style={listItemStyles}
                    onMouseEnter={(e) => e.target.style.backgroundColor = listItemHoverStyles.backgroundColor}
                    onMouseLeave={(e) => e.target.style.backgroundColor = ''}
                    onClick={() => onOptionSelect('openTimeToSkipMenu')}
                >
                    Time to skip
                </li>
                <li
                    className="vjs-menu-item"
                    style={{
                        ...listItemStyles,
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center'
                    }}
                    onMouseEnter={(e) => e.target.style.backgroundColor = listItemHoverStyles.backgroundColor}
                    onMouseLeave={(e) => e.target.style.backgroundColor = ''}
                    onClick={(e) => {
                        e.stopPropagation();
                        onOptionSelect('audioTracks');
                    }}
                >
                    <span style={{ marginRight: '10px' }}>◀</span>
                    <span>Audio Track</span>
                </li>
                <li
                    className="vjs-menu-item"
                    style={listItemStyles}
                    onMouseEnter={(e) => e.target.style.backgroundColor = listItemHoverStyles.backgroundColor}
                    onMouseLeave={(e) => e.target.style.backgroundColor = ''}
                    onClick={() => onOptionSelect('Option 3')}
                >
                    Option 3
                </li>
            </ul>
        </div>
    );
});

export default SettingsMenu;
