import React, { useState } from 'react';
import { Box, TextField, Button, List, ListItem, ListItemText, Checkbox, IconButton } from '@mui/material';
import SaveIcon from '@mui/icons-material/Save';
import BookmarksIcon from '@mui/icons-material/Bookmarks';
import AddIcon from '@mui/icons-material/Add';

const TagSettings = ({ tags, onAddTag, onUpdateTags, selectedTag, setSelectedTag, selectedItems, setSelectionMode }) => {

    const [newTag, setNewTag] = useState('');

    const handleAddTag = () => {
        if (newTag.trim() && !tags.includes(newTag.trim())) {
            onAddTag(newTag.trim());
            setNewTag('');
        }
    };

    const handleTagClick = (tag) => {
        if (selectedTag === tag) {
            setSelectedTag(null);         // Зняти вибір
            setSelectionMode(false);      // Вимкнути селектмод
        } else {
            setSelectedTag(tag);          // Вибрати тег
        }
    };

    return (
        <Box sx={{ position:"fixed", top: "50%", right: 20, transform: "translateY(-50%)", width: '300px', padding: '1rem', backgroundColor: 'rgba(0, 0, 0, 0.5)', borderRadius: '4px' }}>
            <List>
                {tags.map((tag) => (
                    <ListItem
                        key={tag}
                        onClick={() => handleTagClick(tag)}
                        sx={{
                            cursor: 'pointer',
                            backgroundColor: selectedTag === tag ? 'primary.main' : 'transparent',
                            color: selectedTag === tag ? 'primary.contrastText' : 'inherit',
                            borderRadius: '4px',
                            mb: 0.5
                        }}
                    >
                        <ListItemText primary={tag} />
                    </ListItem>
                ))}
            </List>
            {selectedTag && selectedItems.length > 0 && (
                <Button
                    variant="contained"
                    color="primary"
                    startIcon={<SaveIcon />}
                    onClick={onUpdateTags}
                >
                    Зберегти
                </Button>
            )}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                <TextField
                    label="Новий тег"
                    fullWidth
                    value={newTag}
                    onChange={(e) => setNewTag(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleAddTag()}
                />
                <IconButton onClick={handleAddTag}>
                    <AddIcon />
                </IconButton>
            </Box>
        </Box>
    );
};

export default TagSettings;