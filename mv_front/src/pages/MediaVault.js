import React, { useState, useEffect } from 'react';
import CatalogCard from '../components/CatalogCard';
import { fetchMetadata, addTagToItems, fetchAllTags} from '../api/metadataAPI';
import { fetchThumbnail } from '../api/thumbnailAPI';
import TagFilter from '../components/TagFilter';
import { Grid2 as Grid, SpeedDial, SpeedDialAction, SpeedDialIcon, CssBaseline, ThemeProvider, createTheme, ButtonGroup, Button, Menu, MenuItem, Fab, Zoom, Dialog, DialogTitle, DialogContent, TextField, IconButton, Checkbox, FormControlLabel, FormGroup, Box } from '@mui/material';
import BookmarksIcon from '@mui/icons-material/Bookmarks';
import AddIcon from '@mui/icons-material/Add';
import OndemandVideoIcon from '@mui/icons-material/OndemandVideo';
import VideocamIcon from '@mui/icons-material/Videocam';
import VideoLibraryIcon from '@mui/icons-material/VideoLibrary';
import CloseIcon from '@mui/icons-material/Close';
import DeleteIcon from '@mui/icons-material/Delete';
import SettingsIcon from '@mui/icons-material/Settings';
import TagSettings from '../components/TagSettings';
import palette from '../theme/palette';
import MVLogo from '../images/MV_Logo2.png';
import background from '../images/background.png';

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
    const [anchorEl, setAnchorEl] = useState(null);
    const [menuVisible, setMenuVisible] = useState(false);
    const [openFabMenu, setOpenFabMenu] = useState(false);
    const [openOnlineSeriesDialog, setOpenOnlineSeriesDialog] = useState(false);

    const [onlineSeriesTitle, setOnlineSeriesTitle] = useState('');
    const [onlineSeriesImageUrl, setOnlineSeriesImageUrl] = useState('');
    const [onlineSeriesEpisodes, setOnlineSeriesEpisodes] = useState('');
    const [seasons, setSeasons] = useState([{ name: 'Сезон 1', episodes: '' }]);

    const [selectedTags, setSelectedTags] = useState([]); // Стан для тегів фільтрації
    const [filterMode, setFilterMode] = useState('include'); // Стан для режиму фільтрації

    const [openTagSettings, setOpenTagSettings] = useState(false);
    const [tags, setTags] = useState([]); // Масив тегів

    const [selectionMode, setSelectionMode] = useState(false);
    const [selectedItems, setSelectedItems] = useState([]);

    const [selectedTag, setSelectedTag] = useState(null); // Стан для вибраного тегу

    const [openSettingsMenu, setOpenSettingsMenu] = useState(false);

    const handleTagSelectForAssignment = (tag) => {
        setSelectedTag(tag);
        setSelectionMode(true);
        setSelectedItems([]);
    };    

    const handleAddTag = (newTag) => {
        setTags((prevTags) => [...prevTags, newTag]);
    };
    
    const handleUpdateTags = async () => {
        if (selectedTag && selectedItems.length > 0) {
            try {
                await addTagToItems(selectedItems, selectedTag); // Додаємо тег до елементів
                const updatedTags = await fetchAllTags(); // Оновлюємо список тегів з API
                setTags(updatedTags); // Оновлюємо стан тегів
            } catch (error) {
                console.error('Не вдалося оновити теги:', error);
            } finally {
                setSelectionMode(false);
                setSelectedItems([]);
                setSelectedTag(null);
            }
        }
    };
    

    useEffect(() => {
        const loadTags = async () => {
            try {
                const fetchedTags = await fetchAllTags();
                setTags(fetchedTags);
            } catch (error) {
                console.error('Не вдалося завантажити теги:', error);
            }
        };
    
        loadTags();
    }, []);

    useEffect(() => {
        const fetchCollections = async () => {
            console.log('Starting fetchCollections...'); // Debugging
            try {
                console.log('Calling fetchMetadata...');
                const data = await fetchMetadata();
                console.log('Metadata fetched:', data); // Debugging
                const { movies = [], series = [], online_series = [] } = data;

                const movieCollections = await Promise.all(
                    movies.map(async (movie) => {
                        try {
                            // console.log(`Fetching thumbnail for movie: ${movie.title}`);
                            const thumbnailUrl = await fetchThumbnail(movie.path);
                            // console.log(`Thumbnail fetched for movie ${movie.title}:`, thumbnailUrl); // Debugging
                            return {
                                id: movie.id,
                                title: movie.title.replace(/\.[^/.]+$/, ""),
                                type: 'movie',
                                partsCount: movie.parts.length,
                                thumbnailUrl,
                                tags: movie.tags || [], // Додаємо теги
                            };
                        } catch (err) {
                            console.error(`Failed to fetch thumbnail for movie ${movie.title}:`, err); // Debugging
                            return {
                                id: movie.id,
                                title: movie.title.replace(/\.[^/.]+$/, ""),
                                type: 'movie',
                                partsCount: movie.parts.length,
                                thumbnailUrl: '',
                                tags: movie.tags || [], // Додаємо теги
                            };
                        }
                    })
                );

                const seriesCollections = await Promise.all(
                    series.map(async (serie) => {
                        try {
                            // console.log(`Fetching thumbnail for series: ${serie.title}`);
                            const thumbnailUrl = await fetchThumbnail(serie.path);
                            // console.log(`Thumbnail fetched for series ${serie.title}:`, thumbnailUrl); // Debugging
                            return {
                                id: serie.id,
                                title: serie.title,
                                type: 'series',
                                partsCount: serie.seasons.length,
                                thumbnailUrl,
                                tags: serie.tags || [], // Додаємо теги
                            };
                        } catch (err) {
                            console.error(`Failed to fetch thumbnail for series ${serie.title}:`, err); // Debugging
                            return {
                                id: serie.id,
                                title: serie.title,
                                type: 'series',
                                partsCount: serie.seasons.length,
                                thumbnailUrl: '',
                                tags: serie.tags || [], // Додаємо теги
                            };
                        }
                    })
                );

                const onlineSeriesCollections = await Promise.all(
                    online_series.map(async (onlineSerie) => {
                        try {
                            // console.log(`Fetching thumbnail for online series: ${onlineSerie.title}`);
                            const thumbnailUrl = onlineSerie.image_url;
                            // console.log(`Thumbnail fetched for online series ${onlineSerie.title}:`, thumbnailUrl); // Debugging
                            return {
                                id: onlineSerie.id,
                                title: onlineSerie.title,
                                type: 'online_series',
                                partsCount: onlineSerie.seasons.length,
                                thumbnailUrl,
                                tags: onlineSerie.tags || [], // Додаємо теги
                            };
                        } catch (err) {
                            console.error(`Failed to fetch thumbnail for online series ${onlineSerie.title}:`, err); // Debugging
                            return {
                                id: onlineSerie.id,
                                title: onlineSerie.title,
                                type: 'online_series',
                                partsCount: onlineSerie.seasons.length,
                                thumbnailUrl: '',
                                tags: onlineSerie.tags || [], // Додаємо теги
                            };
                        }
                    })
                );

                const allCollections = [...movieCollections, ...seriesCollections, ...onlineSeriesCollections];
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
        let filtered = collections;

        if (filter !== 'all') {
            if (filter === 'series_combined') {
                filtered = filtered.filter(collection => collection.type === 'series' || collection.type === 'online_series');
            } else {
                filtered = filtered.filter(collection => collection.type === filter);
            }
        }

        if (selectedTags.length > 0) {
            if (filterMode === 'include') {
                filtered = filtered.filter(collection => selectedTags.some(tag => collection.tags.includes(tag)));
            } else {
                filtered = filtered.filter(collection => !selectedTags.some(tag => collection.tags.includes(tag)));
            }
        }

        setFilteredCollections(filtered);
    }, [filter, collections, selectedTags, filterMode]);

    const handleTagChange = (tag) => {
        setSelectedTags(prevSelectedTags =>
            prevSelectedTags.includes(tag)
                ? prevSelectedTags.filter(t => t !== tag)
                : [...prevSelectedTags, tag]
        );
    };      

    const toggleFilterMode = () => {
        setFilterMode(prevMode => (prevMode === 'include' ? 'exclude' : 'include'));
    };

    const handleSeriesMenuEnter = () => {
        setMenuVisible(true);
    };

    const handleSeriesMenuLeave = () => {
        setMenuVisible(false);
    };

    const handleSeriesMenuClick = (event) => {
        setAnchorEl(event.currentTarget);
    };

    const handleSeriesMenuClose = () => {
        setAnchorEl(null);
    };

    const handleFabClick = () => {
        setOpenFabMenu(!openFabMenu);
    };

    const handleOpenOnlineSeriesDialog = () => {
        setOpenOnlineSeriesDialog(true);
        setOpenFabMenu(false);
    };

    const handleCloseOnlineSeriesDialog = () => {
        setOpenOnlineSeriesDialog(false);
        setOnlineSeriesTitle('');
        setOnlineSeriesImageUrl('');
        setOnlineSeriesEpisodes('');
    };

    const updateSeasonName = (index, value) => {
        const updatedSeasons = [...seasons];
        updatedSeasons[index].name = value;
        setSeasons(updatedSeasons);
    };

    const updateSeasonEpisodes = (index, value) => {
        const updatedSeasons = [...seasons];
        updatedSeasons[index].episodes = value;
        setSeasons(updatedSeasons);
    };

    const addSeason = () => {
        const newSeason = { name: `Сезон ${seasons.length + 1}`, episodes: '' };
        setSeasons([...seasons, newSeason]);
    };

    const removeSeason = (index) => {
        const updatedSeasons = seasons.filter((_, i) => i !== index);
        setSeasons(updatedSeasons);
    };

    if (loading) return <div>Loading...</div>;
    if (error) return <div>{error}</div>;

    const addOnlineSeries = <>
        <Dialog open={openOnlineSeriesDialog} onClose={handleCloseOnlineSeriesDialog} maxWidth="sm" fullWidth>
            <DialogTitle>
                Add Online Series
                <IconButton 
                aria-label="close" 
                onClick={handleCloseOnlineSeriesDialog} 
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
                value={onlineSeriesTitle} 
                onChange={(e) => setOnlineSeriesTitle(e.target.value)}
                />
                <TextField 
                label="Image URL" 
                fullWidth 
                margin="normal" 
                value={onlineSeriesImageUrl} 
                onChange={(e) => setOnlineSeriesImageUrl(e.target.value)}
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
                        onChange={(e) => updateSeasonName(index, e.target.value)}
                    />
                    {index > 0 && (
                        <IconButton 
                        onClick={() => removeSeason(index)} 
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
                    onChange={(e) => updateSeasonEpisodes(index, e.target.value)}
                    />
                </div>
                ))}
                <Button 
                startIcon={<AddIcon />} 
                onClick={addSeason} 
                style={{ marginTop: '1rem', alignSelf: 'flex-start' }}
                >
                Add Season
                </Button>
                <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '1rem' }}>
                <Button 
                    variant="contained" 
                    color="primary" 
                    onClick={() => {
                    console.log('Saving online series:', {
                        title: onlineSeriesTitle,
                        imageUrl: onlineSeriesImageUrl,
                        seasons: seasons.map((season) => ({
                        name: season.name,
                        episodes: season.episodes.split('\n').map((url) => url.trim()).filter(Boolean),
                        })),
                    });
                    handleCloseOnlineSeriesDialog();
                    }}
                >
                    Save
                </Button>
                </div>
            </DialogContent>
        </Dialog>
    </>

    const gridStyle = {
        justifyContent: openTagSettings ? 'left' : 'center',
    };
    
    return (
        <ThemeProvider theme={darkTheme}>
            <CssBaseline />
            <div style={{ padding: '1rem 2rem', position: 'relative', backgroundImage: `url(${background})`, backgroundRepeat: 'repeat' }}>
                <img src={MVLogo} alt="MediaVault Logo" style={{ display: 'inline-block', marginRight: '1rem', height: '100px' }} />
                {/* <h1 style={{ display: 'inline-block', marginRight: '1rem' }}>MediaVault</h1> */}
                <ButtonGroup variant="contained" style={{ marginBottom: '1rem', float: 'right', backgroundColor: 'rgba(0, 0, 0, 0.5)' }}>
                    <Button onClick={() => setFilter('all')} color={filter === 'all' ? 'primary' : 'default'}>All</Button>
                    <Button onClick={() => setFilter('movie')} color={filter === 'movie' ? 'primary' : 'default'}>Movies</Button>
                    <Button 
                        onClick={() => setFilter('series_combined')}
                        onMouseEnter={handleSeriesMenuEnter}
                        onMouseLeave={handleSeriesMenuLeave}
                        color={filter === 'series_combined' || filter === 'series' || filter === 'online_series' ? 'primary' : 'default'}
                    >
                        Series
                    </Button>
                </ButtonGroup>
                {menuVisible && (
                        <div style={{ position: 'absolute', top: '3.39rem', right: '2.25rem', backgroundColor: 'rgba(0, 0, 0, 0.5)' }}
                            anchorEl={anchorEl}
                            open={Boolean(anchorEl)}
                            onClose={handleSeriesMenuLeave}
                            MenuListProps={{ disablePadding: true }}
                            onMouseEnter={handleSeriesMenuEnter}
                            onMouseLeave={handleSeriesMenuLeave}
                        >
                            <MenuItem onClick={() => { setFilter('series'); handleSeriesMenuLeave(); }}>Local</MenuItem>
                            <MenuItem onClick={() => { setFilter('online_series'); handleSeriesMenuLeave(); }}>Online</MenuItem>
                        </div>
                    )}
                <TagFilter
                    tags={tags}
                    selectedTags={selectedTags}
                    handleTagChange={handleTagChange}
                    filterMode={filterMode}
                    toggleFilterMode={toggleFilterMode}
                />
                <Grid container spacing={2} justifyContent="center" style={gridStyle}>
                    {filteredCollections.map(collection => (
                        <Grid item xs={12} sm={6} md={4} key={collection.id}>
                            <CatalogCard 
                                title={collection.title} 
                                type={collection.type} 
                                partsCount={collection.partsCount} 
                                thumbnailUrl={collection.thumbnailUrl} 
                                link={'/player/' + collection.id}
                                showCheckbox={selectionMode}
                                isSelected={selectedItems.includes(collection.id)}
                                onSelect={() => {
                                    setSelectedItems(prev =>
                                        prev.includes(collection.id) ? prev.filter(id => id !== collection.id) : [...prev, collection.id]
                                    );
                                }}
                            />
                        </Grid>
                    ))}
                </Grid>

                <SpeedDial
                    ariaLabel="Settings"
                    icon={<SettingsIcon />}
                    direction="up"
                    onClick={() => setOpenSettingsMenu((prev) => !prev)} // Перемикає відкриття по кліку
                    open={openSettingsMenu} // Визначає, чи відкритий SpeedDial
                    style={{ position: 'fixed', bottom: '2rem', right: '2rem' }}
                >
                    <SpeedDialAction
                        icon={<BookmarksIcon />}
                        tooltipTitle="Tag Settings"
                        onClick={() => {setOpenTagSettings(!openTagSettings); setOpenSettingsMenu(false);}}
                    />
                    <SpeedDialAction
                        icon={<AddIcon />}
                        tooltipTitle="Add Online Series"
                        onClick={() => {handleOpenOnlineSeriesDialog(); setOpenSettingsMenu(false);}}
                    />
                    
                </SpeedDial>
                {openTagSettings && (
                    <TagSettings
                        tags={tags}
                        onAddTag={handleAddTag}
                        onUpdateTags={() => handleUpdateTags(selectedItems, selectedTag)}
                        selectedTag={selectedTag}
                        setSelectedTag={handleTagSelectForAssignment} // Використовуємо нову функцію
                        selectedItems={selectedItems}
                    />
                )}
            </div>
        </ThemeProvider>
    );
};

export default MediaVault;

