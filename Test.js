function generateArrayWithSum(inputSize) {
    if (inputSize <= 0) {
        throw new Error("Input size must be a positive integer.");
    }
    
    // Initialize an array with random numbers
    let numbers = Array.from({ length: inputSize }, () => Math.floor(Math.random() * 100));
    
    // Calculate the current sum of the numbers
    let currentSum = numbers.reduce((acc, num) => acc + num, 0);
    
    // Calculate the difference needed to make the sum 100
    let difference = 100 - currentSum;
    
    // Adjust the last element to make the sum exactly 100
    numbers[numbers.length - 1] += difference;

    // Ensure no element exceeds 100 or becomes negative (if needed)
    numbers = numbers.map(num => Math.max(0, Math.min(num, 100)));
    
    // In case the last adjustment made the sum slightly off, correct it
    let finalSum = numbers.reduce((acc, num) => acc + num, 0);
    if (finalSum !== 100) {
        numbers[numbers.length - 1] += (100 - finalSum);
    }

    return numbers;
}

// Example usage:
console.log(generateArrayWithSum(5));
