import React, { useState } from "react";

import { fetchMediaStructurePerview } from "../../api/mediaAPI";

import { Dialog, DialogTitle, DialogContent, IconButton } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';

import AddMediaWizardStepFolderSelect from "./AddMediaDialogComponents/AddMediaWizardStepFolderSelect";
import AddMeidaWizardStepCommit from "./AddMediaDialogComponents/AddMeidaWizardStepCommit";

const styles = {
    'dialog':{
        maxHeight: '80vh', 
        minHeight: '20vh',
        display: "flex",
        flexDirection: "column",
    },
    'content':{
        flex: 1,
        display: "flex",
        flexDirection: "column",
        overflow: "hidden"
    }
}

const AddMediaDialog = ({ open, onClose, onSave, listOfMedia }) => {
    const [currentStep, setCurrentStep] = useState(0);
    const [selectedFolderPath, setSelectedFolderPath] = useState('');
    const [currentMediaStructurePreview, setCurrentMediaStructurePreview] = useState({});
    
    const handleMediaStructurePreview = async (path) => {
        try{
            const mediaStructurePerview = await fetchMediaStructurePerview(path);
            setCurrentMediaStructurePreview(mediaStructurePerview);
            console.log(mediaStructurePerview);
        }
        catch (e){
            console.log("Data get failed: ", e);
        }
    }

    const setFuncForWizard = [
        (data) => {
            setSelectedFolderPath(data)
            handleMediaStructurePreview(data)
        }, 
        () => {}
    ]

    const nextWizardStep = (data) => {
        setFuncForWizard[currentStep](data)
        setCurrentStep(currentStep+1)
    }

    const stepProceed = [
        <AddMediaWizardStepFolderSelect onProceed={nextWizardStep} listOfMedia={listOfMedia} />,
        <AddMeidaWizardStepCommit currentMediaStructurePreview={currentMediaStructurePreview} onProceed={nextWizardStep} />,
    ]

    return (
        <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth sx={styles.dialog} PaperProps={{ sx: { maxHeight: "80vh", minHeight: "20vh", display: "flex", flexDirection: "column", }}}>
            <DialogTitle>
                Add Media
                <IconButton
                    aria-label="close"
                    onClick={onClose}
                    style={{ position: 'absolute', right: 8, top: 8 }}
                    >
                        <CloseIcon />
                </IconButton>
            </DialogTitle>

            <DialogContent style={styles.content}>
                {stepProceed[currentStep]}
            </DialogContent>
        </Dialog>
    );
};

export default AddMediaDialog;