const updateMultipleItems = (array, updates) => {
  return array.map(outerObj => {
    // Check if the outer object's key matches any of the updates
    const matchedUpdates = updates.filter(update => update.outerKey === outerObj.key);
    
    if (matchedUpdates.length > 0) {
      return {
        ...outerObj,
        subSection: outerObj.subSection.map(subObj => {
          // Check if the subSection object's key matches any of the updates
          const subSectionUpdates = matchedUpdates.filter(update => update.subSectionKey === subObj.key);

          if (subSectionUpdates.length > 0) {
            return {
              ...subObj,
              items: subObj.items.map(itemObj => {
                // Check if the current item matches any of the updates
                const updateForItem = subSectionUpdates.find(update => update.targetItemKey === itemObj.key);
                
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

// Example usage: Update multiple items
const updates = [
  { outerKey: 'outerKey1', subSectionKey: 'subKey1', targetItemKey: 'targetKey1', newData: 'newValue1' },
  { outerKey: 'outerKey2', subSectionKey: 'subKey2', targetItemKey: 'targetKey2', newData: 'newValue2' },
];

const updatedData = updateMultipleItems(data, updates);
console.log(updatedData);
