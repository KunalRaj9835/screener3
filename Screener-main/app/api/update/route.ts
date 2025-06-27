import { NextRequest, NextResponse } from 'next/server';
import { readCSV, writeCSV, StockData } from '../../../utils/csvHandler';

export async function POST(request: NextRequest) {
  try {
    const { action, data } = await request.json();
    let currentData = readCSV();
    
    switch (action) {
      case 'add':
        currentData.push(data);
        break;
      case 'update':
        const index = currentData.findIndex(item => item.id === data.id);
        if (index !== -1) {
          currentData[index] = { ...currentData[index], ...data };
        }
        break;
      case 'delete':
        currentData = currentData.filter(item => item.id !== data.id);
        break;
      default:
        return NextResponse.json(
          { error: 'Invalid action' },
          { status: 400 }
        );
    }
    
    const success = writeCSV(currentData);
    if (success) {
      return NextResponse.json({ message: 'Data updated successfully' });
    } else {
      return NextResponse.json(
        { error: 'Failed to update data' },
        { status: 500 }
      );
    }
  } catch (error) {
    return NextResponse.json(
      { error: 'Server error' },
      { status: 500 }
    );
  }
}