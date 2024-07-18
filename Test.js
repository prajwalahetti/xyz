// Function to create a map from json2 array
function createMapFromJson2(json2) {
    let map = {};
    json2.forEach(obj => {
        Object.keys(obj).forEach(key => {
            map[key] = obj[key];
        });
    });
    return map;
}

// Function to replace values in json1 with values from json2 map
function replaceValues(json1, json2Map) {
    // Helper function to recursively traverse and replace values in the nested JSON
    function traverseAndReplace(obj, json2Map) {
        for (let key in obj) {
            // Check if the current value is an object and not null
            if (typeof obj[key] === 'object' && obj[key] !== null) {
                // Recursively process nested objects and arrays
                traverseAndReplace(obj[key], json2Map);
            } else {
                // Replace value if it matches a key in json2 map
                if (json2Map.hasOwnProperty(obj[key])) {
                    obj[key] = json2Map[obj[key]];
                }
            }
        }
    }

    // Clone json1 to avoid mutating the original object
    let clonedJson1 = JSON.parse(JSON.stringify(json1));

    // Traverse and replace values
    traverseAndReplace(clonedJson1, json2Map);

    return clonedJson1;
}

// Create map from json2 array
let json2Map = createMapFromJson2(json2);

// Replace values and print the result
let result = replaceValues(json1, json2Map);
console.log(JSON.stringify(result, null, 2));
