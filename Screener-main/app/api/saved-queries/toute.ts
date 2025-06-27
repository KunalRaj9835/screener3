import { NextRequest, NextResponse } from 'next/server';

// This would typically connect to your database
// For demo purposes, we'll use a simple in-memory store
let savedQueries: any[] = [];

export async function GET() {
  try {
    return NextResponse.json({ queries: savedQueries });
  } catch (error) {
    return NextResponse.json({ error: 'Failed to fetch saved queries' }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { name, description, filters, sortConfig, resultCount, totalCount } = body;
    
    if (!name) {
      return NextResponse.json({ error: 'Query name is required' }, { status: 400 });
    }

    const newQuery = {
      id: Date.now().toString(),
      name,
      description: description || '',
      filters: filters || {},
      sortConfig: sortConfig || null,
      resultCount: resultCount || 0,
      totalCount: totalCount || 0,
      timestamp: new Date().toISOString(),
      createdAt: new Date().toISOString()
    };

    savedQueries.push(newQuery);

    return NextResponse.json({ 
      message: 'Query saved successfully', 
      query: newQuery 
    });
  } catch (error) {
    return NextResponse.json({ error: 'Failed to save query' }, { status: 500 });
  }
}

export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const id = searchParams.get('id');
    
    if (!id) {
      return NextResponse.json({ error: 'Query ID is required' }, { status: 400 });
    }

    savedQueries = savedQueries.filter(query => query.id !== id);

    return NextResponse.json({ message: 'Query deleted successfully' });
  } catch (error) {
    return NextResponse.json({ error: 'Failed to delete query' }, { status: 500 });
  }
}