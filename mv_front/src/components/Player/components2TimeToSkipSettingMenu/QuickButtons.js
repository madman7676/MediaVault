import React from 'react';
import { Box, IconButton, Tooltip } from '@mui/material';
import { KeyboardTab, Pause } from '@mui/icons-material';
import { buttonSizeStyles } from '../../../styles/TimeToSkipSettingsMenu.styles';

export default function QuickButtons({ field, handleSetToStart, handleSetToCurrentTime, handleSetToEnd }) {
    return (
        <Box display="inline-flex" gap={1} justifyContent="center" alignItems="center">
            <Tooltip title="To Start">
                <IconButton onClick={() => handleSetToStart(field)} sx={buttonSizeStyles}>
                    <KeyboardTab sx={{ transform: 'rotate(180deg)' }} />
                </IconButton>
            </Tooltip>
            <Tooltip title="Current Time">
                <IconButton onClick={() => handleSetToCurrentTime(field)} sx={buttonSizeStyles}>
                    <Pause />
                </IconButton>
            </Tooltip>
            <Tooltip title="To End">
                <IconButton onClick={() => handleSetToEnd(field)} sx={buttonSizeStyles}>
                    <KeyboardTab />
                </IconButton>
            </Tooltip>
        </Box>
    );
}