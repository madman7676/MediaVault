// TimeToSkipSettingsMenu.js: Component for managing timeToSkip intervals
import React, { useState, useEffect, useRef } from 'react';
import { Box, Typography, List, ListItem, IconButton } from '@mui/material';
import { Add, Close, Save, SaveAlt, } from '@mui/icons-material';

import { processBookmarksChangeLog, processBulkUpdateforBookmarksChangeLog } from '../../api/bookmarksAPI';

import IntervalsForm from './components2TimeToSkipSettingMenu/IntervalsForm';
import IntervalItem from './components2TimeToSkipSettingMenu/IntervalItem';
import { containerStyles, closeButtonStyles } from '../../styles/TimeToSkipSettingsMenu.styles';

import { formatTime, parseTimeInput, sortIntervals } from '../../utils/timeUtils';
import { useBookmarksChangeLog } from '../../hooks/playerHooks/useBookmarksChangeLog';


const TimeToSkipSettingsMenu = ({ intervals: initialIntervals, onIntervalsChange, onClose, currentEpisodeId, pendingTemplate }) => {
    const [intervals, setIntervals] = useState(initialIntervals);
    const [editingIndex, setEditingIndex] = useState(null);
    const [editInterval, setEditInterval] = useState({ start: '', end: '' });
    const [isAdding, setIsAdding] = useState(false);
    const containerRef = useRef(null);
    const { bookmarksChangeLog, setBookmarksChangeLog, manageBookmarksChangeLog } = useBookmarksChangeLog();


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

    useEffect(() => {
        if (pendingTemplate) {
            const newInterval = { start: formatTime(pendingTemplate.start), end: formatTime(pendingTemplate.end), id: `Temp-${Date.now()}` };
            handleAddInterval(newInterval);
        }
    }, [pendingTemplate?.timeSpamp]);

    const handleAddInterval = (currentInterval) => {
        if (currentInterval.start && currentInterval.end) {
            const id = manageBookmarksChangeLog('CREATE', parseTimeInput(currentInterval.start), parseTimeInput(currentInterval.end));

            const updatedIntervals = sortIntervals([...intervals, { start: parseTimeInput(currentInterval.start), end: parseTimeInput(currentInterval.end), id }]);
            setIntervals(updatedIntervals);
            setEditInterval({ start: '', end: '' });
            setIsAdding(false);
            setEditingIndex(null);
        }
    };

    const handleSaveEdit = (currentInterval) => {
        if (editingIndex !== null && currentInterval.start && currentInterval.end) {
            const updatedIntervals = sortIntervals(intervals.map((interval, index) =>
                index === editingIndex ? { start: parseTimeInput(currentInterval.start), end: parseTimeInput(currentInterval.end), id: interval.id } : interval
            ));
            setIntervals(updatedIntervals);
            manageBookmarksChangeLog('UPDATE', parseTimeInput(currentInterval.start), parseTimeInput(currentInterval.end), intervals[editingIndex].id);
            setEditingIndex(null);
            setEditInterval({ start: '', end: '' });
        }
    };

    const handleDeleteInterval = (index) => {
        const updatedIntervals = sortIntervals(intervals.filter((_, i) => i !== index));
        setIntervals(updatedIntervals);
        // onIntervalsChange(updatedIntervals);
        manageBookmarksChangeLog('DELETE', null, null, intervals[index].id);
    };

    const handleSaveToServer = async () => {
        try {
            const resp = await processBookmarksChangeLog(currentEpisodeId, bookmarksChangeLog);
            console.log('Intervals saved to server successfully.');
            // Оновлення локальних інтервалів з новими ID для створених інтервалів
            let tempIdToNewIdMap = {};
            resp.forEach(result => {
                if (result.status === 'success' && result.action === 'CREATE') {
                    tempIdToNewIdMap[result.id] = result.result.id;
                }
            });
            const updatedIntervals = intervals.map(interval => {
                if (interval.id.startsWith('Temp-') && tempIdToNewIdMap[interval.id]) {
                    return { ...interval, id: tempIdToNewIdMap[interval.id] };
                }
                return interval;
            });
            setIntervals(updatedIntervals);
            onIntervalsChange(updatedIntervals); // Збереження локально після успішного збереження на сервері
            setBookmarksChangeLog({});
        } catch (error) {
            console.error('Failed to save intervals to server:', error);
        }
    };

    const handleBulkUpdate = async () => { // Нотатка: Оновити функцію під нову архітектуру
        try {
            await processBulkUpdateforBookmarksChangeLog(currentEpisodeId, bookmarksChangeLog);
            console.log('Intervals updated successfully.');
            onIntervalsChange(intervals);
            setBookmarksChangeLog({});
        } catch (error) {
            console.error('Failed to update intervals:', error);
        }
    };

    const handleEditInterval = (index) => {
        const interval = intervals[index];
        setEditInterval({ start: formatTime(interval.start), end: formatTime(interval.end) });
        setEditingIndex(index);
    };

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
                            <IntervalsForm
                                isAdding={false}
                                editInterval={{ start: formatTime(interval.start), end: formatTime(interval.end) }}
                                setEditInterval={setEditInterval}
                                handleAddInterval={handleAddInterval}
                                handleSaveEdit={handleSaveEdit}
                                setEditingIndex={setEditingIndex}
                                setIsAdding={setIsAdding}
                            />
                        ) : (
                            <IntervalItem 
                                interval={interval} 
                                index={index} 
                                handleEditInterval={handleEditInterval} 
                                handleDeleteInterval={handleDeleteInterval} 
                            />
                        )}
                    </ListItem>
                ))}
                {isAdding && (
                    <ListItem>
                        <IntervalsForm
                            isAdding={true}
                            editInterval={editInterval}
                            setEditInterval={setEditInterval}
                            handleAddInterval={handleAddInterval}
                            handleSaveEdit={handleSaveEdit}
                            setEditingIndex={setEditingIndex}
                            setIsAdding={setIsAdding}
                        />
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
