const updateItems = (array, outerKey, subSectionKey, updates) => {
  return array.map(outerObj => {
    // Check if the outer object's key matches the constant outer key
    if (outerObj.key === outerKey) {
      return {
        ...outerObj,
        subSection: outerObj.subSection.map(subObj => {
          // Check if the subSection object's key matches the constant subSection key
          if (subObj.key === subSectionKey) {
            return {
              ...subObj,
              items: subObj.items.map(itemObj => {
                // Check if the current item's key matches any of the target keys in updates
                const updateForItem = updates.find(update => update.targetItemKey === itemObj.key);
                
                // If a match is found, update the data property
                return updateForItem ? { ...itemObj, data: updateForItem.newData } : itemObj;
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

// Example usage: Update multiple items for constant outerKey and subKey
const outerKey = 'outerKey1';
const subSectionKey = 'subKey1';
const updates = [
  { targetItemKey: 'targetKey1', newData: 'newValue1' },
  { targetItemKey: 'targetKey2', newData: 'newValue2' },
];

const updatedData = updateItems(data, outerKey, subSectionKey, updates);
console.log(updatedData);
