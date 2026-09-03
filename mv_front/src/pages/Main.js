import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import palette from '../styles/theme/palette';
import { 
  Grid2 as Grid, 
  CssBaseline, 
  ThemeProvider, 
  createTheme, 
  Box
} from '@mui/material';

import CatalogCard from '../components/CatalogCard';

// import { fetchAllMedia } from '../api/mediaAPI';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    background: {
      default: palette.background.page,
      paper: palette.background.paper,
    },
    text: {
      primary: palette.text.lightPrimary,
      secondary: palette.text.lightSecondary,
    },
  },
});

const Main = () => {
  const [collections, setCollections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [selectionMode, setSelectionMode] = useState(false);
  const [selectedItems, setSelectedItems] = useState([]);

  const letterRefs = useRef({});

  const handleItemSelection = useCallback((id) => {
    setSelectedItems(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]);
  }, []);

  // prepare letter refs (one ref per first-letter)
  useMemo(() => {
    letterRefs.current = {};
    collections.forEach(item => {
      const first = item.title?.[0]?.toUpperCase();
      if (first && !letterRefs.current[first]) {
        letterRefs.current[first] = React.createRef();
      }
    });
  }, [collections]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>{error}</div>;

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Box sx={{ padding: 2 }}>
        <Grid container spacing={2} justifyContent="center">
          {(() => {
            const usedLetters = new Set();
            return collections.map(collection => {
              const first = collection.title?.[0]?.toUpperCase();
              let ref = null;
              if (first && letterRefs.current[first] && !usedLetters.has(first)) {
                ref = letterRefs.current[first];
                usedLetters.add(first);
              }
              return (
                <Grid
                  item
                  xs={12}
                  sm={6}
                  md={4}
                  key={collection.id}
                  ref={ref}
                >
                  <CatalogCard
                    title={collection.title}
                    type={collection.type ?? 'media'}
                    partsCount={collection.partsCount ?? 0}
                    thumbnailUrl={collection.img_path ?? collection.thumbnailUrl ?? ''}
                    link={'/player/' + collection.id}
                    showCheckbox={selectionMode}
                    isSelected={selectedItems.includes(collection.id)}
                    onSelect={() => handleItemSelection(collection.id)}
                    tags={collection.tags ?? []}
                  />
                </Grid>
              );
            });
          })()}
        </Grid>
      </Box>
    </ThemeProvider>
  );
};

export default Main;
