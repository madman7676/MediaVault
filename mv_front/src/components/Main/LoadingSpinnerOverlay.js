import React from "react";
import { Backdrop, CircularProgress, Box, Typography } from "@mui/material";
import palette from "../../styles/theme/palette";

const LoadingSpinnerOverlay = ({ loading, error }) => {
  return (
    <Backdrop open={loading} style={{ zIndex: 1300, color: '#fff' }}>
        <Box textAlign="center">
            <CircularProgress color="inherit" />
            {error ? (
                <Typography variant="h6" color="error" sx={{ mt: 2 }}>
                    {error}
                </Typography>
            ) : null}
        </Box>
    </Backdrop>
  );
};

export default LoadingSpinnerOverlay;