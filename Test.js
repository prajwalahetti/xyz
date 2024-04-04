 Function to clean up and parse the dates
function cleanAndParseDates(dates) {
    const cleanedDates = dates.map(date => date.trim().replace(/'/g, ''));
    return cleanedDates.map(date => new Date(date));
}

// Function to convert date to numerical value (total minutes since midnight)
function dateToMinutes(date) {
    const hours = date.getUTCHours();
    const minutes = date.getUTCMinutes();
    return hours * 60 + minutes; // Convert hours to minutes and add minutes
}

// Function to calculate mean (average) of an array of numbers
function calculateMean(arr) {
    const sum = arr.reduce((acc, val) => acc + val, 0);
    return sum / arr.length;
}

// Function to calculate standard deviation of an array of numbers
function calculateStandardDeviation(arr) {
    const mean = calculateMean(arr);
    const squaredDifferences = arr.map(val => Math.pow(val - mean, 2));
    const variance = calculateMean(squaredDifferences);
    return Math.sqrt(variance);
}

// Function to calculate mean and standard deviation of an array of dates
function calculateMeanAndStandardDeviation(dates) {
    // Clean and parse the dates
    const cleanedDates = cleanAndParseDates(dates);

    // Convert dates to numerical values (total minutes since midnight)
    const minutes = cleanedDates.map(dateToMinutes);

    // Calculate mean and standard deviation
    const mean = calculateMean(minutes);
    const standardDeviation = calculateStandardDeviation(minutes);

    return {
        mean: mean,
        standardDeviation: standardDeviation
    };
}

// Example usage
const dates = [
    '2024-03-29T00:26:00.000Z',
    '2024-03-28T00:30:00.000Z',
    '2024-03-27T00:28:00.000Z',
    '2024-03-26T00:35:00.000Z',
    '2024-03-25T11:17:00.000Z'
];

const result = calculateMeanAndStandardDeviation(dates);
console.log("Mean:", result.mean);
console.log("Standard Deviation:", result.standardDeviation);
