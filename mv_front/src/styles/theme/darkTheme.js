import { createTheme } from "@mui/material";

import palette from './palette';

// Створюємо тему один раз за межами компонента
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    background: {
      default: palette.background.page,
      paper: palette.background.paper,
    },
    text: {
      primary: palette.text.lightPrimary,
      secondary: palette.text.lightSecondary,
    },
  },
});

export default darkTheme;