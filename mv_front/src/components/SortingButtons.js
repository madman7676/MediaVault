import { FormGroup, FormControlLabel, Checkbox, Button, Box } from '@mui/material';
import SortIcon from '@mui/icons-material/Sort';
import SvgIcon from '@mui/material/SvgIcon';
import SortByAlphaIcon from '@mui/icons-material/SortByAlpha';

const SortSwapVertIcon = (props) => {
  const x1 = 2.5, y1 = 6, x2 = 5.5, y2 = 16.5;

  return (
    <SvgIcon {...props} viewBox="0 0 20 20">
      <path d={`M${x1} ${y1 + 1.5} L${x1 + 1.6} ${y1} l1.5 1.5`}
            stroke="currentColor" strokeWidth="1" strokeLinecap="round"/>
      <rect x={x1 + 1} y={y1} width="1.25" height="10" rx="0.75" fill="currentColor"/>
      <path d={`M${x2} ${y2} L${x2 + 1.5} ${y2 + 1.5} l1.5 -1.5`}
            stroke="currentColor" strokeWidth="1" strokeLinecap="round"/>
      <rect x={x2 + 0.875} y={y2 - 9} width="1.25" height="10" rx="0.75" fill="currentColor"/>
      <rect x="10" y="6.25" width="8" height="1.25" rx="0.625" fill="currentColor"/>
      <rect x="10" y="11.25" width="10" height="1.25" rx="0.625" fill="currentColor"/>
      <rect x="10" y="16.25" width="12" height="1.25" rx="0.625" fill="currentColor"/>
    </SvgIcon>
  );
};


const SortingButtons = ({ sortBy, setSortBy }) => {

    return (
        <Box 
            className="sorting-buttons" 
            sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                flexDirection: 'column', 
                padding: '0.5rem', 
                flexShrink: 0 
            }}>
            
            <Button
                variant="contained"
                color="secondary"
                fontSize="small"
                sx={{ minWidth: '24px', width: '24px', height: '24px', mb: '2px' }}
                // onClick={() => setSortBy('date')}
            >
                <SortIcon sx={{ fontSize: '14px' }} />
            </Button>
            <Button
                variant="contained"
                color="secondary"
                fontSize="small"
                sx={{ minWidth: '24px', width: '24px', height: '24px' }}
                // onClick={() => setSortBy('alpha')}
            >
                <SortSwapVertIcon style={{ fontSize: '14px', width: 14, height: 14 }} />
            </Button>
        </Box>
    )
}

export default SortingButtons;