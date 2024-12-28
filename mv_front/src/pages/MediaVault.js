// MediaVault component using CatalogCard
import React, { useState, useEffect } from 'react';
import CatalogCard from '../components/CatalogCard';
import { fetchMetadata } from '../api/metadataAPI';
import { fetchThumbnail } from '../api/thumbnailAPI';
import { Grid, CssBaseline, ThemeProvider, createTheme, ButtonGroup, Button } from '@mui/material';
import palette from '../theme/palette';

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

const MediaVault = () => {
    const [collections, setCollections] = useState([]);
    const [filteredCollections, setFilteredCollections] = useState([]);
    const [filter, setFilter] = useState('all');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchCollections = async () => {
            console.log('Starting fetchCollections...'); // Debugging
            try {
                console.log('Calling fetchMetadata...');
                const data = await fetchMetadata();
                console.log('Metadata fetched:', data); // Debugging
                const { movies = [], series = [] } = data;

                const movieCollections = await Promise.all(
                    movies.map(async (movie) => {
                        try {
                            console.log(`Fetching thumbnail for movie: ${movie.title}`);
                            const thumbnailUrl = await fetchThumbnail(movie.path);
                            console.log(`Thumbnail fetched for movie ${movie.title}:`, thumbnailUrl); // Debugging
                            return {
                                id: movie.id,
                                title: movie.title,
                                type: 'movie',
                                partsCount: movie.parts.length,
                                thumbnailUrl,
                            };
                        } catch (err) {
                            console.error(`Failed to fetch thumbnail for movie ${movie.title}:`, err); // Debugging
                            return {
                                id: movie.id,
                                title: movie.title,
                                type: 'movie',
                                partsCount: movie.parts.length,
                                thumbnailUrl: '',
                            };
                        }
                    })
                );

                const seriesCollections = await Promise.all(
                    series.map(async (serie) => {
                        try {
                            console.log(`Fetching thumbnail for series: ${serie.title}`);
                            const thumbnailUrl = await fetchThumbnail(serie.path);
                            console.log(`Thumbnail fetched for series ${serie.title}:`, thumbnailUrl); // Debugging
                            return {
                                id: serie.id,
                                title: serie.title,
                                type: 'series',
                                partsCount: serie.seasons.length,
                                thumbnailUrl,
                            };
                        } catch (err) {
                            console.error(`Failed to fetch thumbnail for series ${serie.title}:`, err); // Debugging
                            return {
                                id: serie.id,
                                title: serie.title,
                                type: 'series',
                                partsCount: serie.seasons.length,
                                thumbnailUrl: '',
                            };
                        }
                    })
                );

                const allCollections = [...movieCollections, ...seriesCollections];
                setCollections(allCollections);
                setFilteredCollections(allCollections);
            } catch (err) {
                console.error('Error fetching metadata:', err); // Debugging
                setError('Failed to load collections. Ensure API is returning valid JSON.');
            } finally {
                setLoading(false);
            }
        };

        fetchCollections();
    }, []);

    useEffect(() => {
        if (filter === 'all') {
            setFilteredCollections(collections);
        } else {
            setFilteredCollections(collections.filter(collection => collection.type === filter));
        }
    }, [filter, collections]);

    if (loading) return <div>Loading...</div>;
    if (error) return <div>{error}</div>;

    return (
        <ThemeProvider theme={darkTheme}>
            <CssBaseline />
            <div style={{ padding: '2rem' }}>
                <h1 style={{ display: 'inline-block', marginRight: '1rem' }}>MediaVault</h1>
                <ButtonGroup variant="contained" style={{ marginBottom: '1rem', float: 'right' }}>
                    <Button onClick={() => setFilter('all')} color={filter === 'all' ? 'primary' : 'default'}>All</Button>
                    <Button onClick={() => setFilter('movie')} color={filter === 'movie' ? 'primary' : 'default'}>Movies</Button>
                    <Button onClick={() => setFilter('series')} color={filter === 'series' ? 'primary' : 'default'}>Series</Button>
                </ButtonGroup>
                <Grid container spacing={2} justifyContent="center">
                    {filteredCollections.map(collection => (
                        <Grid item xs={12} sm={6} md={3} key={collection.id}>
                            <CatalogCard 
                                title={collection.title} 
                                type={collection.type} 
                                partsCount={collection.partsCount} 
                                thumbnailUrl={collection.thumbnailUrl} 
                                link={'/player/' + collection.id}
                            />
                        </Grid>
                    ))}
                </Grid>
            </div>
        </ThemeProvider>
    );
};

export default MediaVault;
