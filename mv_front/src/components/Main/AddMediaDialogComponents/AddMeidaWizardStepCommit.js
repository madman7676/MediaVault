import React from "react";
import ReactJson from 'react-json-view'

import { Box, IconButton } from '@mui/material';
import SaveIcon from '@mui/icons-material/Save';

const styles = {
    'mainBox':{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        width: '100%',
        overflow: "hidden", // важливо
    },
    'jsonBox':{
        display: "flex",
        flexDirection: "column",
        fontSize: '16px',
        
        // 1. Дозволяємо контейнеру рости і обмежуємо його
        flexGrow: 1,
        minHeight: 0, // Важливо для Flex-контейнерів
        maxHeight:'10%'
    },
    'json':{
        maxWidth: '100%',
        
        // 2. Додаємо прокрутку
        overflowY: 'auto', 
        
        // 3. 🪄 Приховуємо скролбар (для WebKit, Chrome, Safari)
        '&::-webkit-scrollbar': {
            display: 'none',
        },
        // Приховуємо для Edge/IE та Firefox
        msOverflowStyle: 'none', 
        scrollbarWidth: 'none',
    }
}

const AddMeidaWizardStepCommit = ({ currentMediaStructurePreview, newMediaData, onProceed }) => {
    
    return (
        <Box sx={styles.mainBox}>
            <Box sx={styles.jsonBox}>
                <Box sx={styles.json}>
                    <ReactJson
                        src={currentMediaStructurePreview}
                        theme='bright:inverted'
                        collapsed={1}
                        
                    />
                </Box>
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', marginTop: '1rem' }}>
                <IconButton
                    variant="contained"
                    color="primary"
                    onClick={() => onProceed()}
                >
                    <SaveIcon fontSize="large" />
                </IconButton>
            </Box>
        </Box>
    );
};

export default AddMeidaWizardStepCommit;