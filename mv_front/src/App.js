import React, { useEffect, useState } from "react";
import MediaVault from "./pages/MediaVault";
import CatalogCard from "./components/CatalogCard";
import Player from "./pages/Player";
import AppRouter from "./routers";

function App() {
    return (
        <AppRouter />
    );
}

export default App;
