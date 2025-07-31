// To run this script:
// 1. Install luxon and fs with: npm install luxon csv-parser csv-writer
// 2. Place input.csv in the same directory
// 3. Run using: node script.js

const fs = require('fs');
const path = require('path');
const { DateTime } = require('luxon');
const csv = require('csv-parser');
const createCsvWriter = require('csv-writer').createObjectCsvWriter;

const INPUT_CSV = 'input.csv';
const OUTPUT_CSV = 'output_utc.csv';
const UNMATCHED_TXT = 'unmatched_timestamps.txt';
const ERROR_LOG = 'error_log.txt';
const TIMESTAMP_COLUMN = 'timestamp';

// Specify columns to keep
const COLUMNS_TO_KEEP = ['id', 'name', TIMESTAMP_COLUMN];

const unmatchedEntries = [];
const results = [];
const errorLog = [];

const parseToUTC = (text) => {
  if (!text || typeof text !== 'string' || text.trim() === '') {
    return { original: text, result: null, error: 'Empty or null' };
  }

  text = text.trim();

  // Custom format: "21-MAR-25 2.07.06.4343 AM"
  const customRegex = /^(\d{1,2})-([A-Z]{3})-(\d{2}) (\d{1,2})\.(\d{2})\.(\d{2})\.(\d{1,6}) (AM|PM)$/i;
  const customMatch = text.match(customRegex);

  if (customMatch) {
    const [_, day, monthAbbr, year, hour, minute, second, ms, ampm] = customMatch;
    const fullYear = parseInt(year, 10) + (parseInt(year) < 50 ? 2000 : 1900);
    const cleanString = `${day}-${monthAbbr}-${fullYear} ${hour}:${minute}:${second}.${ms} ${ampm}`;
    const parsed = DateTime.fromFormat(cleanString, 'd-MMM-yyyy h:mm:ss.SSSS a', { zone: 'UTC' });
    return parsed.isValid
      ? { original: text, result: parsed.toUTC().toISO(), error: null }
      : { original: text, result: null, error: 'Invalid parsed result' };
  }

  // Normalize generic formats
  const cleaned = text.replace(/GMT/gi, '+0000').replace(/\s+/g, ' ');

  const autoParsed = DateTime.fromISO(cleaned, { setZone: true });
  if (autoParsed.isValid) {
    return { original: text, result: autoParsed.toUTC().toISO(), error: null };
  }

  return { original: text, result: null, error: 'Unparsable format' };
};

fs.createReadStream(INPUT_CSV)
  .pipe(csv())
  .on('data', (row) => {
    const filteredRow = Object.fromEntries(
      Object.entries(row).filter(([key]) => COLUMNS_TO_KEEP.includes(key))
    );

    const original = filteredRow[TIMESTAMP_COLUMN];
    const { result, error } = parseToUTC(original);
    if (result) {
      results.push({ ...filteredRow, utc: result });
    } else {
      unmatchedEntries.push(original);
      errorLog.push(`Failed to parse: ${original} | Error: ${error}`);
      results.push({ ...filteredRow, utc: '' });
    }
  })
  .on('end', () => {
    // Write parsed CSV
    const headers = Object.keys(results[0] || {}).map((key) => ({ id: key, title: key }));
    const writer = createCsvWriter({ path: OUTPUT_CSV, header: headers });
    writer.writeRecords(results).then(() => {
      fs.writeFileSync(UNMATCHED_TXT, unmatchedEntries.join('\n'));
      fs.writeFileSync(ERROR_LOG, errorLog.join('\n'));
    });
  });
