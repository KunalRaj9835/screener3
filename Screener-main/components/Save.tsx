'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

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

// Predefined tags library
const PREDEFINED_TAGS = [
  'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'a9', 'a10',
  'a11', 'a12', 'a13', 'a14', 'a15', 'a16', 'a17', 'a18', 'a19', 'a20',
  'a21', 'a22', 'a23', 'a24', 'a25', 'a26', 'a27', 'a28', 'a29', 'a30'
];

// Tag colors for rotation
const TAG_COLORS = [
  '#fde4f8', // Pink
  '#dbf3f8', // Light Blue
  '#dde6fa', // Light Purple
  '#d9f4e5', // Light Green
  '#fbeddc'  // Light Orange
];

export default function SaveQuery() {
  const [queryData, setQueryData] = useState<SavedQuery | null>(null);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [saving, setSaving] = useState(false);
  const [savedQueries, setSavedQueries] = useState<SavedQuery[]>([]);
  const [showSavedQueries, setShowSavedQueries] = useState(false);
  const [showAllTags, setShowAllTags] = useState(false);
  
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    // Get query data from URL parameters
    const dataParam = searchParams.get('data');
    if (dataParam) {
      try {
        const decoded = JSON.parse(decodeURIComponent(dataParam));
        setQueryData(decoded);
        
        // Auto-generate name based on filters
        const filterNames = Object.keys(decoded.filters).filter(key => decoded.filters[key]);
        const autoName = filterNames.length > 0 
          ? `Query with ${filterNames.join(', ')}` 
          : `Stock Query ${new Date().toLocaleDateString()}`;
        setName(autoName);
      } catch (error) {
        console.error('Error parsing query data:', error);
      }
    }

    // Load saved queries from localStorage
    loadSavedQueries();
  }, [searchParams]);

  const loadSavedQueries = () => {
    try {
      const saved = localStorage.getItem('savedStockQueries');
      if (saved) {
        setSavedQueries(JSON.parse(saved));
      }
    } catch (error) {
      console.error('Error loading saved queries:', error);
    }
  };

  const handleTagToggle = (tag: string) => {
    setSelectedTags(prev => 
      prev.includes(tag) 
        ? prev.filter(t => t !== tag)
        : [...prev, tag]
    );
  };

  const getTagColor = (index: number) => {
    return TAG_COLORS[index % TAG_COLORS.length];
  };

  const getTagTextColor = (bgColor: string) => {
    // Return dark text for all these light backgrounds
    return '#374151'; // gray-700
  };

  const saveQuery = async () => {
    if (!queryData || !name.trim()) {
      alert('Please enter a name for your query');
      return;
    }

    setSaving(true);
    
    try {
      const newQuery: SavedQuery = {
        id: Date.now().toString(),
        ...queryData,
        name: name.trim(),
        description: description.trim(),
        tags: selectedTags
      };

      // Save to localStorage
      const existingQueries = JSON.parse(localStorage.getItem('savedStockQueries') || '[]');
      const updatedQueries = [...existingQueries, newQuery];
      localStorage.setItem('savedStockQueries', JSON.stringify(updatedQueries));

      alert('Query saved successfully!');
      router.push('/my-query');
    } catch (error) {
      console.error('Error saving query:', error);
      alert('Error saving query. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const deleteQuery = (id: string) => {
    if (confirm('Are you sure you want to delete this saved query?')) {
      const updatedQueries = savedQueries.filter(q => q.id !== id);
      localStorage.setItem('savedStockQueries', JSON.stringify(updatedQueries));
      setSavedQueries(updatedQueries);
    }
  };

  const loadQuery = (query: SavedQuery) => {
    // Create URL parameters from the saved query
    const searchParams = new URLSearchParams();
    Object.keys(query.filters).forEach(key => {
      if (query.filters[key]) {
        searchParams.append(key, query.filters[key]);
      }
    });
    
    router.push(`/query-results?${searchParams.toString()}`);
  };

  const displayedTags = showAllTags ? PREDEFINED_TAGS : PREDEFINED_TAGS.slice(0, 4);

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <div className="bg-white">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-800">Save Query</h1>
            <button
              onClick={() => router.push('/my-query')}
              className="bg-[#9bec00] hover:bg-[#8dd400] text-white px-6 py-2 rounded-lg font-medium transition-colors"
            >
              My Queries ({savedQueries.length})
            </button>
          </div>
        </div>
      </div>

      {/* Universal Container */}
      <div className="universal-container max-w-4xl mx-auto" style={{ paddingLeft: '6px', paddingRight: '6px', paddingTop: '24px' }}>
        {/* Save Current Query */}
        {queryData && (
          <div className="bg-white rounded-lg p-6 mb-6">
            {/* Query Summary */}
            <div className="mb-6">
              <div className="text-sm text-gray-600 mb-4">
                Query searched: {Object.entries(queryData.filters)
                  .filter(([_, value]) => value)
                  .map(([key, value]) => `${key} = ${value}`)
                  .join(', ') || 'All stocks'}
              </div>
            </div>

            {/* Save Form */}
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium mb-2 text-gray-700">Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-600"
                  placeholder="e.g. Top 50 stocks May 2024"
                />
              </div>

              {/* Tags Selection */}
              <div>
                <label className="block text-sm font-medium mb-3 text-gray-700">Add tags</label>
                
                {/* Tag Container Rectangle */}
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 mb-4 min-h-[60px] flex flex-wrap gap-2 items-start">
                  {selectedTags.length === 0 ? (
                    <span className="text-gray-400 text-sm">No tags selected</span>
                  ) : (
                    selectedTags.map((tag, index) => (
                      <span
                        key={tag}
                        className="inline-flex items-center px-3 py-1 rounded text-sm font-medium"
                        style={{ 
                          backgroundColor: getTagColor(PREDEFINED_TAGS.indexOf(tag)),
                          color: getTagTextColor(getTagColor(PREDEFINED_TAGS.indexOf(tag)))
                        }}
                      >
                        {tag}
                        <button
                          onClick={() => handleTagToggle(tag)}
                          className="ml-2 text-gray-600 hover:text-gray-800"
                        >
                          ×
                        </button>
                      </span>
                    ))
                  )}
                </div>

                {/* Available Tags */}
                <div className="flex flex-wrap gap-2 items-center">
                  {displayedTags.map((tag, index) => (
                    <button
                      key={tag}
                      type="button"
                      onClick={() => handleTagToggle(tag)}
                      className={`px-3 py-1 text-sm rounded font-medium transition-colors ${
                        selectedTags.includes(tag)
                          ? 'ring-2 ring-blue-400 opacity-50'
                          : 'hover:opacity-80'
                      }`}
                      style={{ 
                        backgroundColor: getTagColor(index),
                        color: getTagTextColor(getTagColor(index))
                      }}
                    >
                      {tag}
                    </button>
                  ))}
                  
                  {/* Show More/Less Button */}
                  {PREDEFINED_TAGS.length > 4 && (
                    <button
                      type="button"
                      onClick={() => setShowAllTags(!showAllTags)}
                      className="w-8 h-8 rounded-full bg-gray-200 hover:bg-gray-300 text-gray-600 font-bold transition-colors flex items-center justify-center"
                    >
                      {showAllTags ? '−' : '+'}
                    </button>
                  )}
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2 text-gray-700">Description</label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={4}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-600"
                  placeholder="e.g. Companies with over 20% growth"
                />
              </div>

              <div className="pt-4">
                <button
                  onClick={saveQuery}
                  disabled={saving || !name.trim()}
                  className="bg-[#9bec00] hover:bg-[#8dd400] disabled:bg-gray-400 text-white px-8 py-3 rounded-lg font-medium transition-colors"
                >
                  {saving ? 'Saving...' : 'Save this query'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Recent Saved Queries */}
        {showSavedQueries && (
          <div className="bg-white rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Recent Saved Queries</h2>
            
            {savedQueries.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                No saved queries yet
              </div>
            ) : (
              <div className="space-y-4">
                {savedQueries.slice(0, 5).map((query) => (
                  <div key={query.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="font-medium text-lg">{query.name}</h3>
                        
                        {/* Tags */}
                        {query.tags && query.tags.length > 0 && (
                          <div className="flex flex-wrap gap-2 mt-2">
                            {query.tags.map((tag, index) => (
                              <span
                                key={index}
                                className="inline-block px-2 py-1 rounded text-xs font-medium"
                                style={{ 
                                  backgroundColor: getTagColor(PREDEFINED_TAGS.indexOf(tag)),
                                  color: getTagTextColor(getTagColor(PREDEFINED_TAGS.indexOf(tag)))
                                }}
                              >
                                {tag}
                              </span>
                            ))}
                          </div>
                        )}
                        
                        {query.description && (
                          <p className="text-gray-600 text-sm mt-1">{query.description}</p>
                        )}
                        <div className="text-xs text-gray-500 mt-2 space-y-1">
                          <div>Saved: {new Date(query.timestamp).toLocaleString()}</div>
                          <div>Results: {query.resultCount} of {query.totalCount} stocks</div>
                        </div>
                      </div>
                      <div className="flex space-x-2 ml-4">
                        <button
                          onClick={() => loadQuery(query)}
                          className="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded text-sm transition-colors"
                        >
                          Load
                        </button>
                        <button
                          onClick={() => deleteQuery(query.id!)}
                          className="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded text-sm transition-colors"
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
                {savedQueries.length > 5 && (
                  <div className="text-center">
                    <button
                      onClick={() => router.push('/my-query')}
                      className="text-blue-600 hover:text-blue-700 font-medium"
                    >
                      View all {savedQueries.length} saved queries →
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}