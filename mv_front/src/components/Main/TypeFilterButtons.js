import { ButtonGroup, Button, MenuItem } from "@mui/material";

const TypeFilterButtons = ({ filter, handleFilterChange }) => {
    return (
        <>
            <ButtonGroup 
                variant="contained" 
                className="filter-buttons" 
                style={{ 
                    marginBottom: '1rem', 
                    float: 'right', 
                    backgroundColor: 'rgba(0, 0, 0, 0.5)' 
                }}
            >
                <Button 
                    onClick={() => handleFilterChange('all')}
                    color={filter === 'all' ? 'primary' : 'default'}
                >
                    All
                </Button>
                <Button 
                    onClick={() => handleFilterChange('movie')}
                    color={filter === 'movie' ? 'primary' : 'default'}
                >
                    Movies
                </Button>
                <Button 
                    onClick={() => handleFilterChange('series')}
                    color={
                        filter === 'series' ? 'primary' : 'default'
                    }
                >
                    Series
                </Button>
            </ButtonGroup>

            {/* {filter === 'series' && (
                <div className="series-submenu" style={{ 
                    position: 'absolute', 
                    top: '3.39rem', 
                    right: '2.25rem', 
                    backgroundColor: 'rgba(0, 0, 0, 0.5)' 
                }}>
                    <MenuItem onClick={() => handleFilterChange('series')}>Local</MenuItem>
                    <MenuItem onClick={() => handleFilterChange('online_series')}>Online</MenuItem>
                </div>
            )} */}
        </>
    );
};

export default TypeFilterButtons;