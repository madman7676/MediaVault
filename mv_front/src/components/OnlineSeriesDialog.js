// src/components/OnlineSeriesDialog.js
import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  TextField,
  IconButton,
  Button
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import palette from '../styles/theme/palette';

const OnlineSeriesDialog = ({
  open,
  onClose,
  title,
  onTitleChange,
  imageUrl,
  onImageUrlChange,
  seasons,
  onUpdateSeasonName,
  onUpdateSeasonEpisodes,
  onAddSeason,
  onRemoveSeason,
  onSave
}) => {
  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        Add Online Series
        <IconButton
          aria-label="close"
          onClick={onClose}
          style={{ position: 'absolute', right: 8, top: 8 }}
        >
          <CloseIcon />
        </IconButton>
      </DialogTitle>
      <DialogContent style={{ overflow: 'hidden' }}>
        <TextField
          label="Title"
          fullWidth
          margin="normal"
          value={title}
          onChange={(e) => onTitleChange(e.target.value)}
        />
        <TextField
          label="Image URL"
          fullWidth
          margin="normal"
          value={imageUrl}
          onChange={(e) => onImageUrlChange(e.target.value)}
        />
        <div style={{ display: 'flex', alignItems: 'center', margin: '1rem 0' }}>
          <div style={{ flexGrow: 1, height: '1px', backgroundColor: palette.text.lightSecondary }}></div>
          <span style={{ margin: '0 1rem', color: palette.text.lightPrimary }}>Сезони</span>
          <div style={{ flexGrow: 1, height: '1px', backgroundColor: palette.text.lightSecondary }}></div>
        </div>
        {seasons.map((season, index) => (
          <div key={index} style={{ marginBottom: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '0.5rem' }}>
              <TextField
                label={`Season ${index + 1}`}
                fullWidth
                value={season.name}
                onChange={(e) => onUpdateSeasonName(index, e.target.value)}
              />
              {index > 0 && (
                <IconButton
                  onClick={() => onRemoveSeason(index)}
                  style={{ marginLeft: '0.5rem' }}
                >
                  <DeleteIcon />
                </IconButton>
              )}
            </div>
            <TextField
              label={`Episodes for Season ${index + 1}`}
              fullWidth
              multiline
              rows={4}
              value={season.episodes}
              onChange={(e) => onUpdateSeasonEpisodes(index, e.target.value)}
            />
          </div>
        ))}
        <Button
          startIcon={<AddIcon />}
          onClick={onAddSeason}
          style={{ marginTop: '1rem', alignSelf: 'flex-start' }}
        >
          Add Season
        </Button>
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '1rem' }}>
          <Button
            variant="contained"
            color="primary"
            onClick={onSave}
          >
            Save
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default OnlineSeriesDialog;