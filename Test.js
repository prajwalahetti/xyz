const updateItemByKeys = (array, outerKey, subSectionKey, targetItemKey, newProperties) => {
  return array.map(outerObj => {
    // Check if the outer object's key matches
    if (outerObj.key === outerKey) {
      return {
        ...outerObj,
        subSection: outerObj.subSection.map(subObj => {
          // Check if the subSection object's key matches
          if (subObj.key === subSectionKey) {
            return {
              ...subObj,
              items: subObj.items.map(itemObj => {
                // Check if the current item has the target key
                return itemObj.key === targetItemKey ? { ...itemObj, ...newProperties } : itemObj;
              }),
            };
          }
          return subObj;
        }),
      };
    }
    return outerObj;
  });
};

// Example usage: Update the item with key 'targetKey' in the first outer object and subSection
const updatedData = updateItemByKeys(data, 'outerKey1', 'subKey1', 'targetKey', { key: 'Updated' });
console.log(updatedData);
