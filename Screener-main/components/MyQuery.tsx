'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface SavedQuery {
  id?: string;
  name: string;
  description: string;
  tags: string[];
  filters: { [key: string]: string };
  sortConfig: { key: string; direction: 'asc' | 'desc' } | null;
  timestamp: string;
  resultCount: number;
  totalCount: number;
}

export default function MyQuery() {
  const [savedQueries, setSavedQueries] = useState<SavedQuery[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    loadSavedQueries();
  }, []);

  const loadSavedQueries = () => {
    try {
      const saved = localStorage.getItem('savedStockQueries');
      if (saved) {
        setSavedQueries(JSON.parse(saved));
      }
    } catch (error) {
      console.error('Error loading saved queries:', error);
    } finally {
      setLoading(false);
    }
  };

  const deleteQuery = (id: string) => {
    if (confirm('Are you sure you want to delete this saved query?')) {
      const updatedQueries = savedQueries.filter(q => q.id !== id);
      localStorage.setItem('savedStockQueries', JSON.stringify(updatedQueries));
      setSavedQueries(updatedQueries);
    }
  };

  const runQuery = (query: SavedQuery) => {
    // Create URL parameters from the saved query
    const searchParams = new URLSearchParams();
    Object.keys(query.filters).forEach(key => {
      if (query.filters[key]) {
        searchParams.append(key, query.filters[key]);
      }
    });
    
    router.push(`/query-results?${searchParams.toString()}`);
  };

  const truncateText = (text: string, wordLimit: number = 30): string => {
    const words = text.split(' ');
    if (words.length <= wordLimit) return text;
    return words.slice(0, wordLimit).join(' ') + '...';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin h-12 w-12 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
          <div className="text-lg text-gray-600">Loading saved queries...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-White">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => router.push('/')}
                className="flex items-center text-blue-600 hover:text-blue-700 font-medium transition-colors"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
                New Search
              </button>
              <h1 className="text-2xl font-bold text-gray-800">My Saved Queries</h1>
            </div>
            <div className="text-sm text-gray-600">
              {savedQueries.length} saved {savedQueries.length === 1 ? 'query' : 'queries'}
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto p-6">
        {savedQueries.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-gray-500 text-lg mb-2">No saved queries yet</div>
            <div className="text-gray-400 text-sm mb-6">Start by running a search and saving your query</div>
            <button
              onClick={() => router.push('/')}
              className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg font-medium transition-colors"
            >
              Create Your First Query
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {savedQueries.map((query) => (
              <div key={query.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
                {/* Query Name */}
                <h3 className="font-semibold text-lg text-gray-800 mb-3 line-clamp-2">
                  {query.name}
                </h3>

                {/* Tags */}
                {query.tags && query.tags.length > 0 && (
                  <div className="flex flex-wrap gap-2 mb-3">
                    {query.tags.map((tag, index) => (
                      <span
                        key={index}
                        className="inline-block bg-blue-100 text-blue-800 text-xs font-medium px-2 py-1 rounded"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                )}

                {/* Description */}
                {query.description && (
                  <p className="text-gray-600 text-sm mb-4 leading-relaxed">
                    {truncateText(query.description, 30)}
                  </p>
                )}

                {/* Query Details */}
                <div className="text-xs text-gray-500 mb-4 space-y-1">
                  <div>Created: {new Date(query.timestamp).toLocaleDateString()}</div>
                  <div>Results: {query.resultCount} of {query.totalCount} stocks</div>
                  {Object.keys(query.filters).length > 0 && (
                    <div>
                      Filters: {Object.entries(query.filters)
                        .filter(([_, value]) => value)
                        .map(([key, value]) => `${key}: ${value}`)
                        .join(', ').substring(0, 50)}
                      {Object.entries(query.filters)
                        .filter(([_, value]) => value)
                        .map(([key, value]) => `${key}: ${value}`)
                        .join(', ').length > 50 && '...'}
                    </div>
                  )}
                </div>

                {/* Action Buttons */}
                <div className="flex space-x-2">
                  <button
                    onClick={() => runQuery(query)}
                    className="flex-1 bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                  >
                    Run Query
                  </button>
                  <button
                    onClick={() => deleteQuery(query.id!)}
                    className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}