// MediaVault component using CatalogCard
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import CatalogCard from './components/CatalogCard';
import config from './config.json';
import { Grid2 as Grid, CssBaseline, ThemeProvider, createTheme } from '@mui/material';

const darkTheme = createTheme({
    palette: {
        mode: 'dark',
        background: {
            default: '#121212',
            paper: '#1e1e1e',
        },
        text: {
            primary: '#ffffff',
            secondary: '#bbbbbb',
        },
    },
});

const MediaVault = () => {
    const [collections, setCollections] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchThumbnail = async (videoPath) => {
        try {
            const response = await axios.get(`${config.API_BASE_URL}/api/thumbnail`, {
                params: { video_path: videoPath },
            });
            return response.config.url+"?video_path="+videoPath;
        } catch (err) {
            console.error(`Failed to fetch thumbnail for ${videoPath}:`, err);
            return null;
        }
    };

    useEffect(() => {
        const fetchMetadata = async () => {
            try {
                const response = await axios.get(`${config.API_BASE_URL}/api/metadata`);
                const { movies, series } = response.data;

                const movieCollections = await Promise.all(
                    movies.map(async (movie) => {
                        const thumbnailUrl = await fetchThumbnail(movie.path);
                        return {
                            id: movie.id,
                            title: movie.title,
                            type: 'movie',
                            partsCount: movie.parts.length,
                            thumbnailUrl,
                        };
                    })
                );

                const seriesCollections = await Promise.all(
                    series.map(async (serie) => {
                        const thumbnailUrl = await fetchThumbnail(serie.path);
                        return {
                            id: serie.id,
                            title: serie.title,
                            type: 'series',
                            partsCount: serie.seasons.length,
                            thumbnailUrl,
                        };
                    })
                );

                setCollections([...movieCollections, ...seriesCollections]);
            } catch (err) {
                setError('Failed to load collections.');
            } finally {
                setLoading(false);
            }
        };

        fetchMetadata();
    }, []);

    if (loading) return <div>Loading...</div>;
    if (error) return <div>{error}</div>;

    return (
        <ThemeProvider theme={darkTheme}>
            <CssBaseline />
            <div style={{ padding: '2rem' }}>
                <h1>MediaVault</h1>
                <Grid container spacing={2} justifyContent="center">
                    {collections.map(collection => (
                        <Grid xs={12} sm={6} md={3} key={collection.id}>
                            <CatalogCard 
                                title={collection.title} 
                                type={collection.type} 
                                partsCount={collection.partsCount} 
                                thumbnailUrl={collection.thumbnailUrl} 
                            />
                        </Grid>
                    ))}
                </Grid>
            </div>
        </ThemeProvider>
    );
};

export default MediaVault;
