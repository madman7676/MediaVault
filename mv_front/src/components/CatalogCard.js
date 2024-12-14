// CatalogCard component for Material-UI
import React from 'react';
import { Card, CardContent, Typography, Box, Badge } from '@mui/material';

const CatalogCard = ({ title, type, partsCount, thumbnailUrl }) => {
    const isMovie = type === 'movie';

    return (
        <Card 
            variant="outlined" 
            sx={{ 
                width: 345, 
                height: 400, 
                margin: '1rem', 
                position: 'relative', 
                display: 'flex', 
                flexDirection: 'column', 
                justifyContent: 'space-between', 
                alignItems: 'center', 
                backgroundColor: '#1e1e1e',
            }}
        >
            {/* Thumbnail Image */}
            {thumbnailUrl && (
                <img 
                    src={thumbnailUrl} 
                    alt={`${title} thumbnail`} 
                    style={{ 
                        width: '100%', 
                        height: '100%', 
                        objectFit: 'cover', 
                        borderTopLeftRadius: '4px', 
                        borderTopRightRadius: '4px' 
                    }} 
                />
            )}

            {/* Top Left Label */}
            <Box
                sx={{
                    position: 'absolute',
                    top: 8,
                    left: 8,
                    padding: '2px 6px',
                    border: `1px solid ${isMovie ? 'green' : 'purple'}`,
                    color: isMovie ? 'green' : 'purple',
                    borderRadius: '4px',
                    fontSize: '0.75rem',
                }}
            >
                {isMovie ? 'Фільм' : 'Серіал'}
            </Box>

            {/* Top Right Badge */}
            {partsCount > 1 && (
                <Badge
                    badgeContent={partsCount}
                    sx={{
                        '& .MuiBadge-badge': {
                            backgroundColor: isMovie ? 'green' : 'purple',
                            color: 'white',
                            borderRadius: '8px',
                            padding: '4px 8px',
                            fontSize: '0.75rem',
                        },
                        position: 'absolute',
                        top: 8,
                        right: 8,
                    }}
                />
            )}

            {/* Title at the Bottom */}
            <CardContent
                sx={{
                    position: 'absolute',
                    bottom: 8,
                    width: '100%',
                    textAlign: 'center',
                    backgroundColor: 'rgba(0, 0, 0, 0.7)',
                    padding: '8px',
                }}
            >
                <Typography variant="h6" component="div" color="white">
                    {title}
                </Typography>
            </CardContent>
        </Card>
    );
};

export default CatalogCard;