const containerStyles = {
    position: 'absolute',
    padding: 2,
    backgroundColor: 'white',
    color: 'black',
    borderRadius: 1,
    width: 400,
    maxHeight: '80%',
    overflowY: 'auto',
    zIndex: 1000,
    boxShadow: '0px 4px 10px rgba(0, 0, 0, 0.2)',
};

const closeButtonStyles = {
    position: 'absolute',
    top: 8,
    right: 8,
    backgroundColor: 'red',
    color: 'white',
    '&:hover': {
        backgroundColor: 'darkred',
    },
};

const saveButtonStyles = {
    backgroundColor: 'lightblue',
    '&:hover': {
        backgroundColor: 'transparent',
        border: '1px solid lightblue',
    },
};

const buttonSizeStyles = {
    minWidth: '18px',
    minHeight: '18px',
    padding: '0', // Видаляє додаткові внутрішні відступи
    margin: '0', // Видаляє зовнішні відступи
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    maxHeight: '18px',
    maxWidth: '18px'
};

export { containerStyles, closeButtonStyles, saveButtonStyles, buttonSizeStyles };