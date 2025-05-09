// CatalogCard component for Material-UI
import React from 'react';
import PropTypes from 'prop-types';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, Typography, Box, Badge, Checkbox } from '@mui/material';
import palette from '../styles/theme/palette';

const cardStyles = {
    width: 345,
    height: 400,
    margin: '1rem',
    position: 'relative',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: palette.cardBackground,
    overflow: 'visible', // Allow layers to extend outside
    border: `2px solid ${palette.layerBorder}`,
    borderRadius: '12px', // Rounded corners for the main card
    cursor: 'pointer',
};

const labelStyles = (colors) => ({
    position: 'absolute',
    top: 8,
    left: 8,
    padding: '2px 6px',
    border: `1px solid ${colors.text}`,
    color: colors.text,
    borderRadius: '4px',
    fontSize: '0.75rem',
});

const badgeStyles = (colors) => ({
    '& .MuiBadge-badge': {
        backgroundColor: colors.badge,
        color: 'white',
        width: '32px', // Square size
        height: '32px', // Square size
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        borderRadius: '0 12px 0 12px', // Match card border radius
        fontSize: '1.5rem',
    },
    position: 'absolute',
    top: 16, // Adjust to stay within card boundaries
    right: 16, // Adjust to stay within card boundaries
});

const renderLayers = (isMovie, partsCount) => (
    Array(Math.min(partsCount, 5)).fill().map((_, index) => (
        <Box
            key={index}
            sx={{
                position: 'absolute',
                top: -index * 4, // Offset each layer vertically beneath
                left: -index * 4, // Offset each layer horizontally beneath
                width: '100%', // Keep size consistent
                height: '100%',
                backgroundColor: isMovie ? palette.movie.background : palette.series.background,
                opacity: 0.5,
                boxShadow: `0 0 ${8 + index * 2}px rgba(255, 255, 255, ${0.1 + index * 0.1})`, // Glow effect
                border: `2px solid ${palette.layerBorder}`, // Consistent border for visibility
                borderRadius: '8px',
                zIndex: -index - 1, // Ensure layers stack beneath each other
            }}
        />
    ))
);

const CatalogCard = ({ title, type, partsCount, thumbnailUrl, link, showCheckbox, isSelected, onSelect }) => {
    const isMovie = type === 'movie';
    const colors = isMovie ? palette.movie : palette.series;

    const navigate = useNavigate();

    const handleCardClick = (event) => {
        if (showCheckbox) {
            event.stopPropagation();
            onSelect();
        } else if (link) {
            navigate(link);
        }
    };
  
    return (
        <Card onClick={handleCardClick} variant="outlined" sx={cardStyles}>
            {/* Background Deck Layers */}
            <Box
                sx={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    width: '100%',
                    height: '100%',
                    pointerEvents: 'none', // Prevent interaction
                }}
            >
                {renderLayers(isMovie, partsCount)}
            </Box>

            {/* Thumbnail Image */}
            {thumbnailUrl && (
                <img 
                    src={thumbnailUrl} 
                    alt={`${title} thumbnail`} 
                    style={{ 
                        width: '100%', 
                        height: '100%', 
                        objectFit: 'cover', 
                        borderRadius: '12px' 
                    }} 
                />
            )}

            {/* Top Left Label */}
            <Box sx={labelStyles(colors)}>
                {isMovie ? 'Фільм' : 'Серіал'}
            </Box>

            {/* Top Right Badge */}
            {partsCount > 1 && (
                <Badge badgeContent={partsCount} sx={badgeStyles(colors)} />
            )}

            {/* Title at the Bottom */}
            <CardContent
                sx={{
                    position: 'absolute',
                    bottom: 8,
                    width: '100%',
                    textAlign: 'center',
                    backgroundColor: palette.titleBackground,
                    padding: '8px',
                }}
            >
                <Typography variant="h6" component="div" color="white">
                    {title}
                </Typography>
            </CardContent>
            
            {/* Checkbox (Visible in Selection Mode) */}
            {showCheckbox && (
                <Checkbox
                    checked={isSelected}
                    onClick={(e) => e.stopPropagation()}
                    sx={{
                        position: 'absolute', bottom: 8, right: 8,
                        backgroundColor: 'rgba(0,0,0,0.5)', borderRadius: '50%'
                    }}
                />
            )}
        </Card>
    );
};

CatalogCard.propTypes = {
    title: PropTypes.string.isRequired, // Title is required
    type: PropTypes.oneOf(['movie', 'series']).isRequired, // Must be 'movie' or 'series'
    partsCount: PropTypes.number, // Number of parts is optional
    thumbnailUrl: PropTypes.string, // URL of the thumbnail is optional
    link: PropTypes.string,
    showCheckbox: PropTypes.bool,
    isSelected: PropTypes.bool,
    onSelect: PropTypes.func,
};

CatalogCard.defaultProps = {
    partsCount: 0, // Default parts count is 0
    thumbnailUrl: '', // Default to an empty string if no thumbnail
    link: '',
    showCheckbox: false,
    isSelected: false,
    onSelect: () => {},
};

export default CatalogCard;
