import React, { useRef, useState, useImperativeHandle, forwardRef } from 'react';

const SettingsMenu = forwardRef(({ onOptionSelect, buttonRef }, ref) => {
    const menuRef = useRef(null);
    const menuStyles = {
        position: 'absolute',
        backgroundColor: '#000',
        color: '#fff',
        padding: '10px 5px',
        borderRadius: '4px',
        display: 'block',
        width: 'fit-content',
        right: '0px',
        bottom: '0px',
        marginBottom: '35px',
        pointerEvents: 'auto',
    };

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

    const SettingListItem = (name, option) => {
        return (
            <li
                className="vjs-menu-item"
                style={listItemStyles}
                onMouseEnter={(e) => e.target.style.backgroundColor = listItemHoverStyles.backgroundColor}
                onMouseLeave={(e) => e.target.style.backgroundColor = ''}
                onClick={() => onOptionSelect(option)}
            >
                {name}
            </li>
        );
    }

    const settingsList = [
        { name: 'Time to skip', option: 'openTimeToSkipMenu' },
        { name: 'Fast skipset 0+1:30', option: '0+1:30' },
        { name: 'Fast skipset 0+current', option: '0+current' },
        { name: 'Fast skipset current+1:30', option: 'current+1:30' },
        { name: 'Fast skipset current+end', option: 'current+end' },
    ];

    return (
        <div
            className="vjs-settings-menu"
            ref={menuRef}
            style={menuStyles}
        >
            <ul className="vjs-menu-content" style={listStyles}>
                {settingsList.map((setting) => SettingListItem(setting.name, setting.option))}
            </ul>
        </div>
    );
});

export default SettingsMenu;
