import { Grid2 as Grid } from "@mui/material";

import CatalogCard from '../CatalogCard';

const GridCollection = ({openTagSettings, filteredCollections, letterRefs, selectionMode, selectedItems, handleItemSelection}) => {
    return (
        <Grid
            container
            spacing={2}
            justifyContent="center"
            style={{ justifyContent: openTagSettings ? 'left' : 'center' }}
        >
            {(() => {
            const usedLetters = new Set();
            return filteredCollections.map(collection => {
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
                    type={collection.type}
                    partsCount={collection.partsCount}
                    thumbnailUrl={collection.thumbnailUrl}
                    link={'/player/' + collection.id}
                    showCheckbox={selectionMode}
                    isSelected={selectedItems.includes(collection.id)}
                    onSelect={() => handleItemSelection(collection.id)}
                    tags={collection.tags}
                    />
                </Grid>
                );
            });
            })()}
        </Grid>
    );
};

export default GridCollection;