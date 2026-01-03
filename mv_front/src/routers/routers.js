// router.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import MediaVault from '../pages/MediaVault';
import Player from '../pages/Player';
import Main from '../pages/Main';
import Test from '../pages/test';

const AppRouter = () => {
    return (
        <Router>
            <Routes>
                {/* Головна сторінка */}
                <Route path="/" element={<MediaVault />} />

                {/* Сторінка плеєра з параметром mediaId */}
                <Route path="/player/:mediaId" element={<Player />} />

                <Route path='/test' element={<Test />}/>
            </Routes>
        </Router>
    );
};

export default AppRouter;