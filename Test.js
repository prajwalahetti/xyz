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

  text = text.trim().replace(/GMT/gi, '+0000').replace(/\s+/g, ' ');

  // 1. Native JavaScript Date parse
  const nativeDate = new Date(text);
  if (!isNaN(nativeDate.getTime())) {
    return {
      original: text,
      result: DateTime.fromJSDate(nativeDate).toUTC().toISO(),
      error: null
    };
  }

  // 2. Try known formats
  const knownFormats = [
    'd-MMM-yy h.mm.ss.SSSS a',
    'd-MMM-yy h.mm.ss.SSS a',
    'd-MMM-yyyy h:mm:ss a',
    'd-MMM-yyyy h:mm:ss.SSS a',
    'dd/MM/yyyy HH:mm:ss',
    'yyyy-MM-dd HH:mm:ss',
    'yyyy-MM-ddTHH:mm:ssZ',
    'MM/dd/yyyy h:mm:ss a'
  ];

  for (const format of knownFormats) {
    const parsed = DateTime.fromFormat(text, format, { setZone: true });
    if (parsed.isValid) {
      return { original: text, result: parsed.toUTC().toISO(), error: null };
    }
  }

  // 3. ISO or RFC fallback
  const isoParsed = DateTime.fromISO(text, { setZone: true });
  if (isoParsed.isValid) {
    return { original: text, result: isoParsed.toUTC().toISO(), error: null };
  }

  const rfcParsed = DateTime.fromRFC2822(text, { setZone: true });
  if (rfcParsed.isValid) {
    return { original: text, result: rfcParsed.toUTC().toISO(), error: null };
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
