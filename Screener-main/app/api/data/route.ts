import { NextResponse } from 'next/server';
import { readCSV } from '../../../utils/csvHandler';

export async function GET() {
  try {
    const data = readCSV();
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to fetch data' },
      { status: 500 }
    );
  }
}