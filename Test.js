// Sample input JSON objects
const json1 = {
    "key1": "uniqueValue1",
    "nested": {
        "key2": "uniqueValue2"
    },
    "array": [
        {"key3": "uniqueValue3"},
        {"key4": "uniqueValue4"}
    ]
};

const json2 = {
    "uniqueValue1": "newValue1",
    "uniqueValue2": {
        "subKey": "subValue"
    },
    "uniqueValue3": ["arrayValue1", "arrayValue2"],
    "uniqueValue4": "newValue4"
};

// Function to replace values in json1 with values from json2
function replaceValues(json1, json2) {
    // Helper function to recursively traverse and replace values in the nested JSON
    function traverseAndReplace(obj, json2) {
        for (let key in obj) {
            if (typeof obj[key] === 'object' && obj[key] !== null) {
                traverseAndReplace(obj[key], json2);
            } else {
                if (json2.hasOwnProperty(obj[key])) {
                    obj[key] = json2[obj[key]];
                }
            }
        }
    }

    // Clone json1 to avoid mutating the original object
    let clonedJson1 = JSON.parse(JSON.stringify(json1));

    // Traverse and replace values
    traverseAndReplace(clonedJson1, json2);

    return clonedJson1;
}

// Replace values and print the result
let result = replaceValues(json1, json2);
console.log(JSON.stringify(result, null, 2));
