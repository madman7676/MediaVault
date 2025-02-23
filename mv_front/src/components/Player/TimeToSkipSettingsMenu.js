// TimeToSkipSettingsMenu.js: Component for managing timeToSkip intervals
import React, { useState, useEffect, useRef } from 'react';
import { Box, TextField, Typography, List, ListItem, IconButton, Tooltip } from '@mui/material';
import { Check, Delete, Edit, Add, Close, Save, KeyboardTab, Pause, Cancel, SaveAlt, ArrowUpward, ArrowDownward } from '@mui/icons-material';
import { updateTimeToSkip, bulkUpdateTimeToSkip } from '../../api/metadataAPI';

const containerStyles = {
    position: 'absolute',
    padding: 2,
    backgroundColor: 'white',
    color: 'black',
    borderRadius: 1,
    width: 400,
    maxHeight: '80%',
    overflowY: 'auto',
    zIndex: 1000,
    boxShadow: '0px 4px 10px rgba(0, 0, 0, 0.2)',
};

const closeButtonStyles = {
    position: 'absolute',
    top: 8,
    right: 8,
    backgroundColor: 'red',
    color: 'white',
    '&:hover': {
        backgroundColor: 'darkred',
    },
};

const saveButtonStyles = {
    backgroundColor: 'lightblue',
    '&:hover': {
        backgroundColor: 'transparent',
        border: '1px solid lightblue',
    },
};

const buttonSizeStyles = {
    minWidth: '18px',
    minHeight: '18px',
    padding: '0', // Видаляє додаткові внутрішні відступи
    margin: '0', // Видаляє зовнішні відступи
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    maxHeight: '18px',
    maxWidth: '18px'
};

const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
};

const parseTimeInput = (input) => {
    const parts = input.split(':').map((part) => parseInt(part, 10));
    if (parts.length === 2) {
        return parts[0] * 60 + parts[1];
    }
    return parseInt(input, 10);
};

const TimeToSkipSettingsMenu = ({ intervals: initialIntervals, onIntervalsChange, onClose, currentPath, currentName }) => {
    const [intervals, setIntervals] = useState(initialIntervals);
    const [editingIndex, setEditingIndex] = useState(null);
    const [editInterval, setEditInterval] = useState({ start: '', end: '' });
    const [isAdding, setIsAdding] = useState(false);
    const containerRef = useRef(null);

    useEffect(() => {
        setIntervals(initialIntervals);
    }, [initialIntervals]);

    useEffect(() => {
        const videoElement = document.querySelector('.video-js');
        if (videoElement && containerRef.current) {
            const videoRect = videoElement.getBoundingClientRect();
            const menu = containerRef.current;
            menu.style.top = `${videoRect.top + videoRect.height / 2 - menu.offsetHeight / 2}px`;
            menu.style.left = `${videoRect.left + videoRect.width / 2 - menu.offsetWidth / 2}px`;
        }
    }, []);

    const sortIntervals = (intervalsToSort) => {
        return intervalsToSort.slice().sort((a, b) => a.start - b.start);
    };

    const handleAddInterval = () => {
        if (editInterval.start && editInterval.end) {
            const updatedIntervals = sortIntervals([...intervals, { start: parseTimeInput(editInterval.start), end: parseTimeInput(editInterval.end) }]);
            setIntervals(updatedIntervals);
            setEditInterval({ start: '', end: '' });
            setIsAdding(false);
        }
    };

    const handleCancel = () => {
        setEditingIndex(null);
        setEditInterval({ start: '', end: '' });
        setIsAdding(false);
    };

    const handleSaveEdit = () => {
        if (editingIndex !== null && editInterval.start && editInterval.end) {
            const updatedIntervals = sortIntervals(intervals.map((interval, index) =>
                index === editingIndex ? { start: parseTimeInput(editInterval.start), end: parseTimeInput(editInterval.end) } : interval
            ));
            setIntervals(updatedIntervals);
            setEditingIndex(null);
            setEditInterval({ start: '', end: '' });
        }
    };

    const handleDeleteInterval = (index) => {
        const updatedIntervals = sortIntervals(intervals.filter((_, i) => i !== index));
        setIntervals(updatedIntervals);
        onIntervalsChange(updatedIntervals);
    };

    const handleEditInterval = (index) => {
        const interval = intervals[index];
        setEditInterval({ start: formatTime(interval.start), end: formatTime(interval.end) });
        setEditingIndex(index);
    };

    const handleSaveToServer = async () => {
        try {
            await updateTimeToSkip(currentPath, currentName, intervals);
            console.log('Intervals saved to server successfully.');
            onIntervalsChange(intervals); // Збереження локально після успішного збереження на сервері
        } catch (error) {
            console.error('Failed to save intervals to server:', error);
        }
    };

    const handleBulkUpdate = async () => {
        try {
            await bulkUpdateTimeToSkip(currentPath, currentName, intervals);
            console.log('Intervals updated successfully.');
            onIntervalsChange(intervals); // Збереження локально після успішного збереження на сервері
        } catch (error) {
            console.error('Failed to update intervals:', error);
        }
    };

    const handleSetToStart = (field) => {
        setEditInterval((prev) => ({ ...prev, [field]: '0:00' }));
    };

    const handleSetToCurrentTime = (field) => {
        const videoElement = document.querySelector('.video-js video');
        if (videoElement) {
            const currentTime = Math.floor(videoElement.currentTime);
            setEditInterval((prev) => ({ ...prev, [field]: formatTime(currentTime) }));
        }
    };

    const handleSetToEnd = (field) => {
        const videoElement = document.querySelector('.video-js video');
        if (videoElement) {
            const duration = Math.floor(videoElement.duration);
            setEditInterval((prev) => ({ ...prev, [field]: formatTime(duration) }));
        }
    };

    const handleIncrementTime = (field, increment) => {
        const videoElement = document.querySelector('.video-js video');
        const duration = videoElement ? Math.floor(videoElement.duration) : 0;
        setEditInterval((prev) => {
            let currentTime = parseTimeInput(prev[field]);
            if (isNaN(currentTime)) currentTime = 0; // Обробка порожнього поля
            let newTime = currentTime + increment;
            if (newTime < 0) newTime = 0;
            if (newTime > duration) newTime = duration;
            return { ...prev, [field]: formatTime(newTime) };
        });
    };

    const renderQuickButtons = (field) => (
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

    return (
        <Box ref={containerRef} sx={containerStyles}>
            <IconButton onClick={() => onClose()} sx={closeButtonStyles}>
                <Close />
            </IconButton>
            <Typography variant="h6" gutterBottom>
                TimeToSkip Editor
            </Typography>
            <List>
                {intervals.map((interval, index) => (
                    <ListItem key={index} divider>
                        {editingIndex === index ? (
                            <Box display="flex" gap={1} alignItems="center" width="100%">
                                <Box display="flex" flexDirection="column" gap={1}>
                                    <Box display="flex" alignItems="center">
                                        <TextField
                                            label="Start"
                                            variant="outlined"
                                            size="small"
                                            value={editInterval.start}
                                            onChange={(e) => setEditInterval({ ...editInterval, start: e.target.value })}
                                        />
                                        <Box display="flex" flexDirection="column">
                                            <Tooltip title="Increment Time">
                                                <IconButton onClick={() => handleIncrementTime("start", 1)} sx={buttonSizeStyles}>
                                                    <ArrowUpward />
                                                </IconButton>
                                            </Tooltip>
                                            <Tooltip title="Decrement Time">
                                                <IconButton onClick={() => handleIncrementTime("start", -1)} sx={buttonSizeStyles}>
                                                    <ArrowDownward />
                                                </IconButton>
                                            </Tooltip>
                                        </Box>
                                    </Box>
                                    {renderQuickButtons('start')}
                                </Box>
                                <Box display="flex" flexDirection="column" gap={1}>
                                    <Box display="flex" alignItems="center">
                                        <TextField
                                            label="End"
                                            variant="outlined"
                                            size="small"
                                            value={editInterval.end}
                                            onChange={(e) => setEditInterval({ ...editInterval, end: e.target.value })}
                                        />
                                        <Box display="flex" flexDirection="column">
                                            <Tooltip title="Increment Time">
                                                <IconButton onClick={() => handleIncrementTime("end", 1)} sx={buttonSizeStyles}>
                                                    <ArrowUpward />
                                                </IconButton>
                                            </Tooltip>
                                            <Tooltip title="Decrement Time">
                                                <IconButton onClick={() => handleIncrementTime("end", -1)} sx={buttonSizeStyles}>
                                                    <ArrowDownward />
                                                </IconButton>
                                            </Tooltip>
                                        </Box>
                                    </Box>
                                    {renderQuickButtons('end')}
                                </Box>
                                <Box display="flex" flexDirection="column" gap={1}>
                                    <IconButton onClick={handleSaveEdit} color="primary" sx={saveButtonStyles}>
                                        <Check />
                                    </IconButton>
                                    <IconButton onClick={handleCancel} color="error" sx={saveButtonStyles}>
                                        <Cancel />
                                    </IconButton>
                                </Box>
                            </Box>
                        ) : (
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
                        )}
                    </ListItem>
                ))}
                {isAdding && (
                    <ListItem>
                        <Box display="flex" gap={1} alignItems="center" width="100%">
                            <Box display="flex" flexDirection="column" gap={1}>
                                <Box display="flex" alignItems="center">
                                    <TextField
                                        label="Start"
                                        variant="outlined"
                                        size="small"
                                        value={editInterval.start}
                                        onChange={(e) => setEditInterval({ ...editInterval, start: e.target.value })}
                                    />
                                    <Box display="flex" flexDirection="column">
                                        <Tooltip title="Increment Time">
                                            <IconButton onClick={() => handleIncrementTime("start", 1)} sx={buttonSizeStyles}>
                                                <ArrowUpward />
                                            </IconButton>
                                        </Tooltip>
                                        <Tooltip title="Decrement Time">
                                            <IconButton onClick={() => handleIncrementTime("start", -1)} sx={buttonSizeStyles}>
                                                <ArrowDownward />
                                            </IconButton>
                                        </Tooltip>
                                    </Box>
                                </Box>
                                {renderQuickButtons('start')}
                            </Box>
                            <Box display="flex" flexDirection="column" gap={1}>
                                <Box display="flex" alignItems="center">
                                    <TextField
                                        label="End"
                                        variant="outlined"
                                        size="small"
                                        value={editInterval.end}
                                        onChange={(e) => setEditInterval({ ...editInterval, end: e.target.value })}
                                    />
                                    <Box display="flex" flexDirection="column">
                                        <Tooltip title="Increment Time">
                                            <IconButton onClick={() => handleIncrementTime("end", 1)} sx={buttonSizeStyles}>
                                                <ArrowUpward />
                                            </IconButton>
                                        </Tooltip>
                                        <Tooltip title="Decrement Time">
                                            <IconButton onClick={() => handleIncrementTime("end", -1)} sx={buttonSizeStyles}>
                                                <ArrowDownward />
                                            </IconButton>
                                        </Tooltip>
                                    </Box>
                                </Box>
                                {renderQuickButtons('end')}
                            </Box>
                            <Box display="flex" flexDirection="column" gap={1}>
                                <IconButton onClick={handleAddInterval} color="primary" sx={saveButtonStyles}>
                                    <Check />
                                </IconButton>
                                <IconButton onClick={handleCancel} color="error" sx={saveButtonStyles}>
                                    <Cancel />
                                </IconButton>
                            </Box>
                        </Box>
                    </ListItem>
                )}
                {!isAdding && editingIndex === null && (
                    <ListItem>
                        <IconButton onClick={() => setIsAdding(true)}>
                            <Add />
                        </IconButton>

                        <IconButton onClick={handleBulkUpdate} sx={{ marginLeft: 'auto' }}>
                            <SaveAlt />
                        </IconButton>
                        <IconButton onClick={() => handleSaveToServer()} sx={{ marginLeft: 'auto' }}>
                            <Save />
                        </IconButton>
                    </ListItem>
                )}
            </List>
        </Box>
    );
};

export default TimeToSkipSettingsMenu;
