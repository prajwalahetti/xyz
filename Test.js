function replaceValues(obj1, obj2) {
    // Handle arrays
    if (Array.isArray(obj1)) {
        obj1.forEach((item, index) => {
            if (obj2.hasOwnProperty(item.toString())) {
                obj1[index] = obj2[item.toString()];
            }
        });
    } else if (typeof obj1 === 'object') {
        // Handle objects
        for (let key in obj1) {
            if (obj1.hasOwnProperty(key)) {
                if (typeof obj1[key] === 'object') {
                    replaceValues(obj1[key], obj2);
                } else if (key === 'buttons' && Array.isArray(obj1[key])) {
                    obj1[key] = obj2[obj1[key][0].toString()] || [];
                }
            }
        }
    }
}

// Call the function with json1 and json2
replaceValues(json1, json2);
