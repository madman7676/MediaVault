// FileList.js component for rendering file list
import React, { Fragment } from 'react';
import { List, ListItem, ListItemText, Collapse, Typography } from '@mui/material';
import { ExpandLess, ExpandMore } from '@mui/icons-material';

const FileList = ({
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
            <Typography variant="h6" sx={{ marginBottom: 2, color: palette.text.lightPrimary }}>
                {fileList.length > 0 ? currentTitle : 'No files available'}
            </Typography>
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
