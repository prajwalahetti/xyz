SELECT 
    tablename, 
    (SELECT COUNT(*) FROM public." || tablename || ") AS row_count
FROM pg_tables
WHERE schemaname = 'public' AND tablename IN ('table1', 'table2', 'table3')
ORDER BY row_count DESC;




WITH RECURSIVE fkey_tree AS (
  SELECT
    c.oid::regclass::text AS table_name,
    NULL::text AS depends_on
  FROM pg_class c
  JOIN pg_namespace n ON n.oid = c.relnamespace
  WHERE c.relkind = 'r'  -- only tables
    AND n.nspname NOT IN ('pg_catalog', 'information_schema')

  UNION ALL

  SELECT
    confrelid::regclass::text AS table_name,
    conrelid::regclass::text AS depends_on
  FROM pg_constraint
  WHERE contype = 'f'
), ordered AS (
  SELECT table_name, array_agg(depends_on) AS dependencies
  FROM fkey_tree
  GROUP BY table_name
)
SELECT table_name
FROM ordered
ORDER BY array_length(dependencies, 1) NULLS FIRST;




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
