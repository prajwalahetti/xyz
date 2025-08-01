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
const nameTimeMap = new Map();

const normalizeTimestamp = (text) => {
  if (!text || typeof text !== 'string') return '';
  return text
    .trim()
    .replace(/GMT/gi, '+0000')
    .replace(/([AP]M)$/i, ' $1')
    .replace(/\./g, ':')
    .replace(/([0-9]{4,})/, (m) => m.slice(0, 3))
    .replace(/\s+/g, ' ')
    .toUpperCase();
};

const parseToUTC = (text) => {
  if (!text || typeof text !== 'string' || text.trim() === '') {
    return { original: text, result: null, error: 'Empty or null' };
  }

  text = normalizeTimestamp(text);

  const nativeDate = new Date(text);
  if (!isNaN(nativeDate.getTime())) {
    const dt = DateTime.fromJSDate(nativeDate).toUTC();
    return {
      original: text,
      result: dt.toFormat('dd-MM-yyyy-HH-mm'),
      dt,
      error: null
    };
  }

  const knownFormats = [
    'd-MMM-yy h:mm:ss.SSS a',
    'd-MMM-yy h:mm:ss a',
    'd-MMM-yy h:mm:ss.SSSS a',
    'd-MMM-yyyy h:mm:ss a',
    'd-MMM-yyyy h:mm:ss.SSS a',
    'dd/MM/yyyy HH:mm:ss',
    'yyyy-MM-dd HH:mm:ss',
    'yyyy-MM-ddTHH:mm:ssZ',
    'MM/dd/yyyy h:mm:ss a',
    'd LLL yy HH:mm:ss:SS a ZZZ',
    'd LLL yy h:mm:ss a ZZZ'
  ];

  for (const format of knownFormats) {
    const parsed = DateTime.fromFormat(text, format, { setZone: true });
    if (parsed.isValid) {
      return { original: text, result: parsed.toUTC().toFormat('dd-MM-yyyy-HH-mm'), dt: parsed.toUTC(), error: null };
    }
  }

  const isoParsed = DateTime.fromISO(text, { setZone: true });
  if (isoParsed.isValid) {
    return { original: text, result: isoParsed.toUTC().toFormat('dd-MM-yyyy-HH-mm'), dt: isoParsed.toUTC(), error: null };
  }

  const rfcParsed = DateTime.fromRFC2822(text, { setZone: true });
  if (rfcParsed.isValid) {
    return { original: text, result: rfcParsed.toUTC().toFormat('dd-MM-yyyy-HH-mm'), dt: rfcParsed.toUTC(), error: null };
  }

  return { original: text, result: null, error: 'Unparsable format' };
};

const analyzeCategories = () => {
  const categories = {};
  for (const [name, datetimes] of nameTimeMap.entries()) {
    const filtered = datetimes.filter(dt => dt >= DateTime.utc().minus({ months: 6 }));
    const byWeek = new Map();
    const byMonth = new Map();
    const timestamps = filtered.map(dt => dt.toMillis());

    filtered.forEach(dt => {
      const week = dt.weekYear + '-' + dt.weekNumber;
      const month = dt.toFormat('yyyy-MM');
      if (!byWeek.has(week)) byWeek.set(week, []);
      byWeek.get(week).push(dt);
      if (!byMonth.has(month)) byMonth.set(month, []);
      byMonth.get(month).push(dt);
    });

    const weeks = Array.from(byWeek.keys()).sort();
    const months = Array.from(byMonth.keys()).sort();

    let dailyStreak = 0;
    let weeklyStreak = 0;
    let monthlyStreak = 0;

    for (let i = 0; i < weeks.length - 6; i++) {
      const streakWeeks = weeks.slice(i, i + 7);
      const valid = streakWeeks.every(wk => {
        const days = new Set(byWeek.get(wk).map(dt => dt.weekday));
        return Array.from(days).filter(d => d <= 5).length >= 5;
      });
      if (valid) dailyStreak = 7;
    }

    for (let i = 0; i < weeks.length - 6; i++) {
      const streakWeeks = weeks.slice(i, i + 7);
      const valid = streakWeeks.every(wk => byWeek.get(wk).length >= 1);
      if (valid) weeklyStreak = 7;
    }

    for (let i = 0; i < months.length - 2; i++) {
      const streakMonths = months.slice(i, i + 3);
      const valid = streakMonths.every(m => byMonth.get(m).length >= 1);
      if (valid) monthlyStreak = 3;
    }

    let category = 'none';
    if (dailyStreak >= 7) category = 'daily';
    else if (weeklyStreak >= 7) category = 'weekly';
    else if (monthlyStreak >= 3) category = 'monthly';

    timestamps.sort((a, b) => a - b);
    const gaps = timestamps.slice(1).map((t, i) => (t - timestamps[i]) / (1000 * 60));
    if (gaps.length === 0) {
      categories[name] = { category, median: '', stddev: '' };
      continue;
    }

    gaps.sort((a, b) => a - b);
    const mid = Math.floor(gaps.length / 2);
    const median = gaps.length % 2 === 0 ? (gaps[mid - 1] + gaps[mid]) / 2 : gaps[mid];

    const mean = gaps.reduce((a, b) => a + b, 0) / gaps.length;
    const stddev = Math.sqrt(gaps.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / gaps.length);

    categories[name] = {
      category,
      median: Math.round(median),
      stddev: Math.round(stddev)
    };
  }
  return categories;
};

fs.createReadStream(INPUT_CSV)
  .pipe(csv())
  .on('data', (row) => {
    const filteredRow = Object.fromEntries(
      Object.entries(row).filter(([key]) => COLUMNS_TO_KEEP.includes(key))
    );

    const original = filteredRow[TIMESTAMP_COLUMN];
    const { result, error, dt } = parseToUTC(original);
    if (result && dt) {
      results.push({ ...filteredRow, utc: result });
      const key = filteredRow['name'];
      if (!nameTimeMap.has(key)) nameTimeMap.set(key, []);
      nameTimeMap.get(key).push(dt);
    } else {
      unmatchedEntries.push(original);
      errorLog.push(`Failed to parse: ${original} | Error: ${error}`);
      results.push({ ...filteredRow, utc: '' });
    }
  })
  .on('end', () => {
    const categories = analyzeCategories();
    const finalResults = results.map(row => ({
      ...row,
      category: categories[row.name]?.category || 'unclassified',
      median_minutes: categories[row.name]?.median || '',
      stddev_minutes: categories[row.name]?.stddev || ''
    }));

    const headers = Object.keys(finalResults[0] || {}).map((key) => ({ id: key, title: key }));
    const writer = createCsvWriter({ path: OUTPUT_CSV, header: headers });
    writer.writeRecords(finalResults).then(() => {
      fs.writeFileSync(UNMATCHED_TXT, unmatchedEntries.join('\n'));
      fs.writeFileSync(ERROR_LOG, errorLog.join('\n'));
    });
  });
