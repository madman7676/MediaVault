import React from 'react';
import { Typography, IconButton } from '@mui/material';
import { Edit, Delete } from '@mui/icons-material';
import { formatTime } from '../../../utils/timeUtils';


export default function IntervalItem({ interval, index, handleEditInterval, handleDeleteInterval }) {

    return (
        <>
            <Typography>
                {formatTime(interval.start)} - {formatTime(interval.end)}
            </Typography>
            <IconButton
                onClick={() => handleEditInterval(index)}
                sx={{ marginLeft: 'auto' }}
            >
                <Edit />
            </IconButton>
            <IconButton
                onClick={() => handleDeleteInterval(index)}
                color="error"
            >
                <Delete />
            </IconButton>
        </>
    )
}