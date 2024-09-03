const generateRandomValues = (numValues, totalSum) => {
    if (numValues <= 1) throw new Error("numValues must be greater than 1");
    if (totalSum <= numValues - 1) throw new Error("totalSum must be greater than numValues - 1");

    let values = Array.from({ length: numValues - 1 }, () => Math.floor(Math.random() * (totalSum - (numValues - 1))) + 1);
    values.push(totalSum - values.reduce((a, b) => a + b, 0));

    // Ensure all values are positive
    while (values.some(v => v <= 0)) {
        values = Array.from({ length: numValues - 1 }, () => Math.floor(Math.random() * (totalSum - (numValues - 1))) + 1);
        values.push(totalSum - values.reduce((a, b) => a + b, 0));
    }

    return values;
};

const numValues = 7;
const totalSum = 100;
const randomValues = generateRandomValues(numValues, totalSum);

console.log(randomValues);
console.log('Sum:', randomValues.reduce((a, b) => a + b, 0));  // Verify that the sum is 100
