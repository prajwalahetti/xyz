here

const ExcelJS = require("exceljs");

async function insertImageInCell(workbookPath, sheetName, cellAddress, imagePath, outputPath) {
  const workbook = new ExcelJS.Workbook();

  // Load the existing workbook
  await workbook.xlsx.readFile(workbookPath);
  const worksheet = workbook.getWorksheet(sheetName);

  if (!worksheet) {
    throw new Error(`Sheet "${sheetName}" not found`);
  }

  // Add the image
  const imageId = workbook.addImage({
    filename: imagePath,
    extension: imagePath.endsWith(".png") ? "png" : "jpeg",
  });

  // Convert cell address (like B12) → row/col
  const cell = worksheet.getCell(cellAddress);
  const col = cell.col - 1; // zero-based
  const row = cell.row - 1; // zero-based

  // Insert image at given cell
  worksheet.addImage(imageId, {
    tl: { col, row },
    ext: { width: 100, height: 100 }, // adjust or calculate to fit cell
  });

  // Save to output path (can overwrite workbookPath if needed)
  await workbook.xlsx.writeFile(outputPath || workbookPath);

  console.log(`✅ Image inserted at ${cellAddress} in sheet "${sheetName}"`);
}

// Example usage
insertImageInCell(
  "input.xlsx",   // existing workbook
  "xyz",          // sheet name
  "B12",          // cell address
  "path/to/image.png", // image path
  "output.xlsx"   // output file
).catch(console.error);
