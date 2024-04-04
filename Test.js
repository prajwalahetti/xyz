// Function to convert date to numerical value (total minutes since reference point)
function dateToMinutes(date) {
    return date.getTime() / (1000 * 60); // Convert milliseconds to minutes
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

// Example usage with array of dates
const dates = [
    new Date('2024-03-01T08:00:00'), // Example date 1
    new Date('2024-03-02T12:30:00'), // Example date 2
    new Date('2024-03-03T16:45:00')  // Example date 3
];

// Convert dates to numerical values (total minutes since reference point)
const minutes = dates.map(dateToMinutes);

// Calculate mean and standard deviation
const mean = calculateMean(minutes);
const standardDeviation = calculateStandardDeviation(minutes);

console.log("Mean:", new Date(mean * 60 * 1000)); // Convert mean back to date format if needed
console.log("Standard Deviation:", standardDeviation);









// Function to convert date to numerical value (total minutes since reference point)
function dateToMinutes(date) {
    return date.getTime() / (1000 * 60); // Convert milliseconds to minutes
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

// Function to calculate mean and standard deviation of an array of dates and return them
function calculateMeanAndStandardDeviation(dates) {
    // Convert dates to numerical values (total minutes since reference point)
    const minutes = dates.map(dateToMinutes);

    // Calculate mean and standard deviation
    const mean = calculateMean(minutes);
    const standardDeviation = calculateStandardDeviation(minutes);

    return {
        mean: new Date(mean * 60 * 1000), // Convert mean back to date format
        standardDeviation: standardDeviation
    };
}

// Example usage
const dates = [
    new Date('2024-03-01T08:00:00'), // Example date 1
    new Date('2024-03-02T12:30:00'), // Example date 2
    new Date('2024-03-03T16:45:00')  // Example date 3
];

const { mean, standardDeviation } = calculateMeanAndStandardDeviation(dates);
console.log("Mean:", mean);
console.log("Standard Deviation:", standardDeviation);








// Function to convert date to numerical value (total minutes since midnight)
function dateToMinutes(date) {
    if (!(date instanceof Date)) {
        throw new Error('Input is not a valid Date object');
    }
    const hours = date.getHours();
    const minutes = date.getMinutes();
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

// Function to calculate mean and standard deviation of an array of dates and return them
function calculateMeanAndStandardDeviation(datesArray1, datesArray2) {
    // Concatenate the two arrays of dates
    const allDates = datesArray1.concat(datesArray2);

    // Convert dates to numerical values (total minutes since midnight)
    const minutes = allDates.map(dateToMinutes);

    // Calculate mean and standard deviation
    const mean = calculateMean(minutes);
    const standardDeviation = calculateStandardDeviation(minutes);

    return {
        mean: mean,
        standardDeviation: standardDeviation
    };
}

// Example usage
const datesArray1 = [
    new Date('2024-03-01T08:00:00'), // Example date 1
    new Date('2024-03-02T12:30:00')  // Example date 2
];

const datesArray2 = [
    new Date('2024-03-03T16:45:00')  // Example date 3
];

const { mean, standardDeviation } = calculateMeanAndStandardDeviation(datesArray1, datesArray2);
console.log("Mean:", mean);
console.log("Standard Deviation:", standardDeviation);
