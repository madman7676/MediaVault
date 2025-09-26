import { makeStyles } from '@mui/styles';
import background from '../images/background.png';

const useStyles = makeStyles((theme) => ({
    root: {
        padding: '1rem 2rem',
        position: 'relative',
        backgroundImage: `url(${background})`,
        backgroundRepeat: 'repeat',
        minHeight: '100vh',
    },
    logo: {
        display: 'inline-block',
        marginRight: '1rem',
        height: '100px',
    },
    buttonGroup: {
        marginBottom: '1rem',
        float: 'right',
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
    },
    grid: {
        justifyContent: (props) => (props.openTagSettings ? 'left' : 'center'),
    },
    fab: {
        position: 'fixed',
        bottom: '2rem',
        right: '2rem',
    },
}));

export default useStyles;