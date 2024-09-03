const generateRandomValues = (numValues, totalSum) => {
    let values = Array.from({ length: numValues - 1 }, () => Math.floor(Math.random() * (totalSum - (numValues - 1))) + 1);
    values.push(totalSum - values.reduce((a, b) => a + b, 0));
    return values;
};

const numValues = 7;
const totalSum = 100;
const randomValues = generateRandomValues(numValues, totalSum);

console.log(randomValues);
console.log('Sum:', randomValues.reduce((a, b) => a + b, 0));  // Verify that the sum is 100
