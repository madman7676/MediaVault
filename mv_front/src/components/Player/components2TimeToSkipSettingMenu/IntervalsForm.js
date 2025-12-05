import React, { useEffect, useState } from "react";
import { Box, IconButton, TextField, Tooltip } from "@mui/material";
import { ArrowUpward, ArrowDownward, Check, Cancel } from "@mui/icons-material";

import QuickButtons from "./QuickButtons";
import { buttonSizeStyles, saveButtonStyles } from "../../../styles/TimeToSkipSettingsMenu.styles";
import { formatTime, parseTimeInput } from "../../../utils/timeUtils";

export default function IntervalsForm({
    isAdding,
    editInterval,
    setEditInterval,
    handleAddInterval,
    handleSaveEdit,
    setEditingIndex,
    setIsAdding
}) {
    const [currentInterval, setCurrentInterval] = useState({ start: editInterval.start, end: editInterval.end });

    const handleCancel = () => {
        setEditingIndex(null);
        setCurrentInterval({ start: '', end: '' });
        setEditInterval({ start: '', end: '' });
        setIsAdding(false);
    };

    const handleSetToStart = (field) => {
        setCurrentInterval((prev) => ({ ...prev, [field]: '0:00' }));
    };

    const handleSetToCurrentTime = (field) => {
        const videoElement = document.querySelector('.video-js video');
        if (videoElement) {
            const currentTime = Math.floor(videoElement.currentTime);
            setCurrentInterval((prev) => ({ ...prev, [field]: formatTime(currentTime) }));
        }
    };

    const handleSetToEnd = (field) => {
        const videoElement = document.querySelector('.video-js video');
        if (videoElement) {
            const duration = Math.floor(videoElement.duration);
            setCurrentInterval((prev) => ({ ...prev, [field]: formatTime(duration) }));
        }
    };

    // Додаємо функцію для обробки кнопки "+1:30"
    const handleAddOneThirty = () => {
        const startSeconds = parseTimeInput(currentInterval.start);
        if (!isNaN(startSeconds)) {
            const newEnd = startSeconds + 90;
            setCurrentInterval((prev) => ({ ...prev, end: formatTime(newEnd) }));
        }
    };

    const handleIncrementTime = (field, increment) => {
        const videoElement = document.querySelector('.video-js video');
        const duration = videoElement ? Math.floor(videoElement.duration) : 0;

        let currentTime = parseTimeInput(currentInterval[field]);
        if (isNaN(currentTime)) currentTime = 0; // Обробка порожнього поля
        let newTime = currentTime + increment;
        if (newTime < 0) newTime = 0;
        if (newTime > duration) newTime = duration;
        const newInterval = { ...currentInterval, [field]: formatTime(newTime) };
        setCurrentInterval((prev) => ({ ...prev, [field]: newInterval[field] }));
    };

    const handleConfirmInterval = () => {
        if (isAdding) {
            handleAddInterval(currentInterval);
        } else {
            handleSaveEdit(currentInterval);
        }
        setCurrentInterval({ start: '', end: '' });
    };

    useEffect(() => {
        setCurrentInterval({ start: editInterval.start, end: editInterval.end });
    }, [editInterval]);

    return (
        <Box display="flex" gap={0} alignItems="flex-start" width="100%" flexDirection="column">
            {/* Start column */}
            <Box display="flex" flexDirection="row" alignItems="center" gap={2}>
                <Box display="flex" alignItems="center">
                    <TextField
                        label="Start"
                        variant="outlined"
                        size="small"
                        value={currentInterval.start}
                        onChange={(e) => setCurrentInterval({ ...currentInterval, start: e.target.value })}
                    />
                    <Box display="flex" flexDirection="column" ml={1}>
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
                    <Box display="flex" alignItems="center" ml={1}>
                        <TextField
                            label="End"
                            variant="outlined"
                            size="small"
                            value={currentInterval.end}
                            onChange={(e) => setCurrentInterval({ ...currentInterval, end: e.target.value })}
                        />
                        <Box display="flex" flexDirection="column" ml={1}>
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
                </Box>
            </Box>
            {/* Горизонтальний flex-контейнер для кнопок */}
            <Box display="flex" flexDirection="row" alignItems="center" gap={3}>
                <Box ml={3} display="flex" flexDirection="column">
                    <QuickButtons 
                        field="start" 
                        handleSetToStart={handleSetToStart} 
                        handleSetToCurrentTime={handleSetToCurrentTime} 
                        handleSetToEnd={handleSetToEnd} 
                    />
                </Box>
                <Box display="flex" flexDirection="column" alignItems="center" mt={1} ml={1.5}>
                    <Tooltip title="Set End to Start + 1:30">
                        <IconButton onClick={handleAddOneThirty} sx={{ ...buttonSizeStyles, fontSize: '0.8rem', border: '1px solid #aaa', minHeight: 32, minWidth: 40 }}>
                            +1:30
                        </IconButton>
                    </Tooltip>
                </Box>
                <Box ml={2} display="flex" flexDirection="column">
                    <QuickButtons 
                        field="end" 
                        handleSetToStart={handleSetToStart} 
                        handleSetToCurrentTime={handleSetToCurrentTime} 
                        handleSetToEnd={handleSetToEnd} 
                    />
                </Box>
            </Box>
            {/* Save/Cancel column */}
            <Box display="flex" justifyContent="flex-end" flexDirection="row" gap={1} mt={1} width="100%">
                <IconButton onClick={handleCancel} color="error" sx={saveButtonStyles}>
                    <Cancel />
                </IconButton>
                <IconButton onClick={handleConfirmInterval} color="primary" sx={saveButtonStyles}>
                    <Check />
                </IconButton>
            </Box>
        </Box>
    );
}