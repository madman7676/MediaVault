import React, { useState } from "react";
import { fetchSelectFolder } from "../../../api/selectFolderAPI";
import {
  Box,
  FormControl,
  IconButton,
  InputLabel,
  MenuItem,
  Select,
  Switch,
  TextField,
  Typography,
} from "@mui/material";
import CreateNewFolderIcon from "@mui/icons-material/CreateNewFolder";
import ForwardIcon from "@mui/icons-material/Forward";

/* ==========================================
   Валідація та утилітарні функції
   ========================================== */

const VALIDATION_STATE = {
  VALID: true,
  INVALID: false,
};

const validateForm = (title, selectedFolderPath, isNewMedia, selectedMedia) => ({
  title: title.trim() !== "",
  relatedMedia: isNewMedia || selectedMedia !== "",
  folderPath: selectedFolderPath.trim() !== "",
});

const isFormValid = (validation) => Object.values(validation).every(Boolean);

/* ==========================================
   Стилі
   ========================================== */

const styles = {
  root: { width: "100%", height: "100%" },
  flexRow: { display: "flex", flexDirection: "row" },
  titleField: { width: "60%", flexGrow: 1, m: 1 },
  fullWidth: { width: "100%" },
  toggle: { alignContent: "center", display: "flex", alignItems: "center", m: 1 },
  mediaSection: { m: 1 },
  pathField: { width: "85%", flexGrow: 1, m: 1 },
  pathButton: { alignContent: "center" },
  folderBtn: { alignSelf: "end" },
  proceedRow: { display: "flex", justifyContent: "flex-end", marginTop: "1rem", bottom: 0 },
  menuItem: { display: "block", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" },
};

const menuProps = {
  slotProps: { paper: { style: { maxHeight: 300, width: 250 } } },
  anchorOrigin: { vertical: "bottom", horizontal: "left" },
  transformOrigin: { vertical: "top", horizontal: "left" },
};

/* ==========================================
   Компоненти
   ========================================== */

const MediaSelect = ({ listOfMedia, selectedMedia, setSelectedMedia, isValid }) => (
  <Box sx={styles.mediaSection}>
    <FormControl fullWidth error={!isValid}>
      <InputLabel id="select-media-label">Приналежність до тайтлу</InputLabel>
      <Select
        fullWidth
        displayEmpty
        labelId="select-media-label"
        id="select-media"
        value={selectedMedia}
        label="Приналежність до тайтлу"
        onChange={(e) => setSelectedMedia(e.target.value)}
        MenuProps={menuProps}
      >
        {listOfMedia.map((media) => (
          <MenuItem key={media.id} value={media.id} sx={styles.menuItem}>
            {media.title}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  </Box>
);

const AddMediaWizardStepFolderSelect = ({ onProceed, listOfMedia }) => {
  const [formState, setFormState] = useState({
    title: "",
    selectedFolderPath: "",
    isNewMedia: true,
    selectedMedia: "",
  });

  const [isValid, setIsValid] = useState({
    title: true,
    relatedMedia: true,
    folderPath: true,
  });

  const [isLoading, setIsLoading] = useState(false);

  const { title, selectedFolderPath, isNewMedia, selectedMedia } = formState;

  const handleUpdateForm = (key, value) => {
    setFormState((prev) => ({ ...prev, [key]: value }));
  };

  const handleSelectFolder = async () => {
    setIsLoading(true);
    try {
      const folder = await fetchSelectFolder();
      handleUpdateForm("selectedFolderPath", folder.path);
    } catch (error) {
      console.error("Помилка при виборі папки:", error);
      // Можна додати повідомлення користувачу через snackbar/toast
    } finally {
      setIsLoading(false);
    }
  };

  const handleProceed = () => {
    const validation = validateForm(title, selectedFolderPath, isNewMedia, selectedMedia);
    setIsValid(validation);

    if (isFormValid(validation)) {
      onProceed(selectedFolderPath);
    }
  };

  return (
    <Box sx={styles.root}>
      {/* Рядок з назвою та тумблером */}
      <Box sx={styles.flexRow}>
        <Box sx={styles.titleField}>
          <TextField
            label={isNewMedia ? "Назва тайтлу" : "Назва частини"}
            value={title}
            fullWidth
            onChange={(e) => handleUpdateForm("title", e.target.value)}
            error={!isValid.title}
            helperText={!isValid.title ? "Поле не може бути порожнім" : ""}
          />
        </Box>

        <Box sx={styles.toggle}>
          <Switch
            checked={isNewMedia}
            onChange={(e) => handleUpdateForm("isNewMedia", e.target.checked)}
          />
          <Typography>Новий тайтл</Typography>
        </Box>
      </Box>

      {/* Вибір медіа (показується тільки якщо не новий тайтл) */}
      {!isNewMedia && (
        <MediaSelect
          listOfMedia={listOfMedia}
          selectedMedia={selectedMedia}
          setSelectedMedia={(value) => handleUpdateForm("selectedMedia", value)}
          isValid={isValid.relatedMedia}
        />
      )}

      {/* Вибір папки */}
      <Box sx={styles.flexRow}>
        <Box sx={styles.pathField}>
          <TextField
            label="Шлях до медіа-папки"
            value={selectedFolderPath}
            fullWidth
            slotProps={{ input: { readOnly: true } }}
            error={!isValid.folderPath}
            helperText={!isValid.folderPath ? "Виберіть папку" : ""}
          />
        </Box>

        <Box sx={styles.pathButton}>
          <IconButton
            onClick={handleSelectFolder}
            disabled={isLoading}
            sx={styles.folderBtn}
            aria-label="Вибрати папку"
          >
            <CreateNewFolderIcon fontSize="large" />
          </IconButton>
        </Box>
      </Box>

      {/* Кнопка продовження */}
      <Box sx={styles.proceedRow}>
        <IconButton
          color="primary"
          onClick={handleProceed}
          disabled={isLoading}
          aria-label="Продовжити"
        >
          <ForwardIcon fontSize="large" />
        </IconButton>
      </Box>
    </Box>
  );
};

export default AddMediaWizardStepFolderSelect;