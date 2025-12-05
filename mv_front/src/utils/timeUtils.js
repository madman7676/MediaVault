

const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
};

const parseTimeInput = (input) => {
    const parts = input.split(':').map((part) => parseInt(part, 10));
    if (parts.length === 2) {
        return parts[0] * 60 + parts[1];
    }
    return parseInt(input, 10);
};

const sortIntervals = (intervalsToSort) => {
    return intervalsToSort.slice().sort((a, b) => a.start - b.start);
};

export { formatTime, parseTimeInput, sortIntervals };