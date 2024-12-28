// router.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import MediaVault from '../pages/MediaVault';
import Player from '../pages/Player';

const AppRouter = () => {
    return (
        <Router>
            <Routes>
                {/* Головна сторінка */}
                <Route path="/" element={<MediaVault />} />

                {/* Сторінка плеєра з параметром itemId */}
                <Route path="/player/:itemId" element={<Player />} />
            </Routes>
        </Router>
    );
};

export default AppRouter;