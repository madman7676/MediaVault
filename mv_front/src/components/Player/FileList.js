// FileList.js component for rendering file list
import React, { Fragment } from 'react';
import { List, ListItem, ListItemText, Collapse, Typography, Box } from '@mui/material';
import { ExpandLess, ExpandMore } from '@mui/icons-material';
import { IconButton } from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import { updateFilesPath } from '../../api/metadataAPI';

const FileList = ({
    itemId,
    fileList,
    currentTitle,
    currentFile,
    openSeasons,
    handleToggleSeason,
    handleSelectFile,
    palette,
    lastWatched
}) => {
    
    return (
        <>
            <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                <Typography variant="h6" sx={{ color: palette.text.lightPrimary }}>
                    {fileList.length > 0 ? currentTitle : 'No files available'}
                </Typography>
                <IconButton
                    size="small"
                    onClick={async () => {
                        try {
                            await updateFilesPath(itemId);
                            window.location.reload(); // простий спосіб оновити все
                        } catch (e) {
                            console.error(e);
                        }
                    }}

                    /// TODO: Fix force reload, to normal refresh list

                    sx={{
                        color: palette.primary,
                        backgroundColor: palette.background.paper,
                        border: '1px solid ' + palette.primary,
                        '&:hover': {
                            backgroundColor: palette.primary,
                            color: palette.background.paper,
                        },
                        ml: 1
                    }}
                >
                    <RefreshIcon fontSize="small" />
                </IconButton>
            </Box>
            {fileList.length > 0 && (
                <List>
                    {fileList.map((season, seasonIndex) => (
                        <Fragment key={seasonIndex}>
                            <ListItem disablePadding sx={{ cursor: 'pointer' }} onClick={() => handleToggleSeason(seasonIndex)}>
                                <ListItemText primary={season.seasonTitle} sx={{ color: palette.text.lightPrimary }} />
                                {openSeasons[seasonIndex] ? <ExpandLess /> : <ExpandMore />}
                            </ListItem>
                            <Collapse in={openSeasons[seasonIndex]} timeout="auto" unmountOnExit>
                                {season.files.map((file, fileIndex) => (
                                    <ListItem
                                        key={fileIndex}
                                        button
                                        onClick={() => handleSelectFile(file.url)}
                                        sx={{
                                            cursor: 'pointer',
                                            color:
                                                file.url === currentFile
                                                    ? palette.primary
                                                    : file.url === lastWatched
                                                    ? 'orange'
                                                    : palette.text.lightPrimary,
                                            backgroundColor: currentFile === file.url ? palette.background.paper : 'transparent',
                                            '&:hover': { backgroundColor: palette.secondary, color: palette.text.lightSecondary },
                                            '&:active': { backgroundColor: palette.primary, opacity: 0.8 },
                                        }}
                                    >
                                        <ListItemText primary={file.name} />
                                    </ListItem>
                                ))}
                            </Collapse>
                        </Fragment>
                    ))}
                </List>
            )}
        </>
    );
};

export default FileList;
