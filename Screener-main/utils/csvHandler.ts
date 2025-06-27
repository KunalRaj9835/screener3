import Papa from 'papaparse';
import fs from 'fs';
import path from 'path';

export interface StockData {
  'S.No': number;
  'Name': string;
  'CMP': number;
  'Rs.Cr': number;
  'P/E': number;
  'Mar Cap': number;
  'Qtr Rs.Cr': number;
  'Div Yld %': number;
  'NP Qtr Rs.Cr': number;
  'Qtr Sales Qtr %': number;
  'ROCE %': number;
  [key: string]: any; // For any additional columns
}

const CSV_PATH = path.join(process.cwd(), 'data', 'screener-data.csv');

export function readCSV(): StockData[] {
  try {
    const csvData = fs.readFileSync(CSV_PATH, 'utf8');
    const parsed = Papa.parse(csvData, {
      header: true,
      skipEmptyLines: true,
      dynamicTyping: true,
      delimiter: ',',
      transformHeader: (header: string) => header.trim() // Clean headers
    });
    return parsed.data as StockData[];
  } catch (error) {
    console.error('Error reading CSV:', error);
    return [];
  }
}

export function writeCSV(data: StockData[]): boolean {
  try {
    const csv = Papa.unparse(data);
    fs.writeFileSync(CSV_PATH, csv);
    return true;
  } catch (error) {
    console.error('Error writing CSV:', error);
    return false;
  }
}