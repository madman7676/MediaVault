import React from 'react';
import { FormGroup, FormControlLabel, Checkbox, Button, Box } from '@mui/material';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';

const TagFilter = ({ tags, selectedTags, handleTagChange, filterMode, toggleFilterMode }) => {
    return (
        <Box sx={{ display: 'flex', alignItems: 'center', backgroundColor: 'rgba(0, 0, 0, 0.5)', padding: '0.5rem', borderRadius: '4px' }}>
            <FormGroup row sx={{ flexGrow: 1 }}>
                {[...tags].sort((a, b) => a.localeCompare(b)).map(tag => (
                    <FormControlLabel
                        key={tag}
                        control={
                            <Checkbox
                                checked={selectedTags.includes(tag)}
                                onChange={() => handleTagChange(tag)}
                                name={tag}
                            />
                        }
                        label={tag}
                    />
                ))}
            </FormGroup>
            <Button onClick={toggleFilterMode} variant="contained" color="secondary" sx={{ marginLeft: '1rem' }}>
                {filterMode === 'include' ? <VisibilityIcon /> : <VisibilityOffIcon />}
            </Button>
        </Box>
    );
};

export default TagFilter;