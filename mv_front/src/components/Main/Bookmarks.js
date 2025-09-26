import React from 'react';
import { Box, List, ListItem, ListItemButton, Typography } from '@mui/material';

const Bookmarks = ({ letters, onLetterClick }) => (
  <Box sx={{
    position: 'fixed',
    bottom: 0,
    left: 0,
    zIndex: 10,
    height: '80vh',
    width: 40,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    bgcolor: 'rgba(0, 0, 0, 0.4)',
    borderRadius: 2,
    py: 1,
    overflowY: 'auto',
    scrollbarWidth: 'none',
    '&::-webkit-scrollbar': {
      display: 'none'
    },
    transform: 'translateX(-28px)',
    '&:hover': {
        transform: 'translateX(0)',
        boxShadow: 3,
      },
  }}>
    <List dense>
      {letters.map(letter => (
        <ListItem key={letter} disablePadding>
          <ListItemButton onClick={() => onLetterClick(letter)}>
            <Typography variant="body2" color="text.secondary">{letter}</Typography>
          </ListItemButton>
        </ListItem>
      ))}
    </List>
  </Box>
);

export default Bookmarks;