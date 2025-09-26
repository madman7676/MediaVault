import { SpeedDial, SpeedDialAction } from "@mui/material";
import BookmarksIcon from '@mui/icons-material/Bookmarks';
import AddIcon from '@mui/icons-material/Add';
import SettingsIcon from '@mui/icons-material/Settings';


const SettingsFloatButton = ({onClickSettingsButton, openSettingsMenu, handleTagSettings, handleOpenOnlineSeriesDialog}) => {
    return (
        <SpeedDial
            ariaLabel="Settings"
            icon={<SettingsIcon />}
            direction="up"
            onClick={onClickSettingsButton}
            open={openSettingsMenu}
            className="settings-dial"
            style={{ position: 'fixed', bottom: '2rem', right: '2rem' }}
        >
            <SpeedDialAction
                icon={<BookmarksIcon />}
                tooltipTitle="Tag Settings"
                onClick={handleTagSettings}
            />
            <SpeedDialAction
                icon={<AddIcon />}
                tooltipTitle="Add Online Series"
                onClick={handleOpenOnlineSeriesDialog}
            />
        </SpeedDial>
    );
};

export default SettingsFloatButton;