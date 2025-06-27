'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

interface StockData {
  [key: string]: any;
}

interface Filters {
  [key: string]: string;
}

export default function QueryResult() {
  const [data, setData] = useState<StockData[]>([]);
  const [filters, setFilters] = useState<Filters>({});
  const [loading, setLoading] = useState(true);
  const [sortConfig, setSortConfig] = useState<{
    key: string;
    direction: 'asc' | 'desc';
  } | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 20;
  
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    // Get search parameters from URL
    const urlFilters: Filters = {};
    searchParams.forEach((value, key) => {
      urlFilters[key] = value;
    });
    setFilters(urlFilters);
    
    // Fetch data
    fetchData();
  }, [searchParams]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/data');
      const result = await response.json();
      setData(result);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
    setLoading(false);
  };

  const applyFilters = (): StockData[] => {
    return data.filter(item => {
      return Object.keys(filters).every(key => {
        if (!filters[key]) return true;
        const itemValue = item[key];
        return itemValue?.toString().toLowerCase().includes(filters[key].toLowerCase());
      });
    });
  };

  const sortData = (data: StockData[]): StockData[] => {
    if (!sortConfig) return data;

    return [...data].sort((a, b) => {
      const aValue = a[sortConfig.key];
      const bValue = b[sortConfig.key];
      
      if (typeof aValue === 'number' && typeof bValue === 'number') {
        return sortConfig.direction === 'asc' ? aValue - bValue : bValue - aValue;
      }
      
      const aStr = aValue?.toString() || '';
      const bStr = bValue?.toString() || '';
      
      if (sortConfig.direction === 'asc') {
        return aStr.localeCompare(bStr);
      } else {
        return bStr.localeCompare(aStr);
      }
    });
  };

  const handleSort = (key: string) => {
    let direction: 'asc' | 'desc' = 'asc';
    if (sortConfig && sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  const formatNumber = (value: any): string => {
    if (typeof value !== 'number') return value?.toString() || '';
    
    if (value >= 10000000) {
      return `₹${(value / 10000000).toFixed(2)}Cr`;
    } else if (value >= 100000) {
      return `₹${(value / 100000).toFixed(2)}L`;
    } else if (value >= 1000) {
      return `₹${(value / 1000).toFixed(2)}K`;
    }
    
    return value.toLocaleString('en-IN');
  };

  // Generate dynamic subtitle based on filters
  const generateSubtitle = (): string => {
    if (Object.keys(filters).length === 0) {
      return 'All stocks';
    }
    
    const filterDescriptions = Object.entries(filters)
      .filter(([key, value]) => value && value.trim() !== '')
      .map(([key, value]) => `${key} = ${value}`);
    
    return filterDescriptions.length > 0 
      ? filterDescriptions.join(' & ') 
      : 'All stocks';
  };

  // Export to CSV function
  const exportToCSV = () => {
    const filteredData = sortData(applyFilters());
    
    if (filteredData.length === 0) {
      alert('No data to export');
      return;
    }

    const columns = Object.keys(filteredData[0]);
    
    // Create CSV content
    const csvContent = [
      // Header row
      columns.join(','),
      // Data rows
      ...filteredData.map(row => 
        columns.map(col => {
          const value = row[col];
          // Handle commas and quotes in data
          if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
            return `"${value.replace(/"/g, '""')}"`;
          }
          return value;
        }).join(',')
      )
    ].join('\n');

    // Create and download file
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `stock-query-results-${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Save query function
  const saveQuery = () => {
    const queryData = {
      filters,
      sortConfig,
      timestamp: new Date().toISOString(),
      resultCount: applyFilters().length,
      totalCount: data.length
    };

    // Navigate to save page with query data
    const encodedData = encodeURIComponent(JSON.stringify(queryData));
    router.push(`/save-query?data=${encodedData}`);
  };

  const handleMyQueries = () => {
    router.push('/my-query');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin h-12 w-12 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
          <div className="text-lg text-gray-600">Loading stock data...</div>
        </div>
      </div>
    );
  }

  const filteredAndSortedData = sortData(applyFilters());
  const columns = data.length > 0 ? Object.keys(data[0]) : [];
  
  // Pagination logic
  const totalPages = Math.ceil(filteredAndSortedData.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentData = filteredAndSortedData.slice(startIndex, endIndex);

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  return (
    <div className="min-h-screen bg-white pl-45 pr-20">
      {/* Main content - full width */}
      <div className="p-6">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-800 mb-1">Query Results</h1>
              <p className="text-gray-600">{generateSubtitle()}</p>
              <p className="text-sm text-gray-500">{filteredAndSortedData.length} results found: Showing page {currentPage} of {totalPages}</p>
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={exportToCSV}
                className="bg-white border border-gray-300 hover:bg-gray-50 text-black px-4 py-2 rounded font-medium transition-colors"
              >
                Export
              </button>
              <button
                onClick={saveQuery}
                className="bg-[#9bec00] hover:bg-[#8bc400] text-white px-4 py-2 rounded font-medium transition-colors"
              >
                Save this query
              </button>
              <button
                onClick={handleMyQueries}  
                className="bg-white border border-gray-300 hover:bg-gray-50 text-black px-4 py-2 rounded font-medium transition-colors"
              >
                My Queries
              </button>
            </div>
          </div>
        </div>

        {/* Results Table */}
        <div className="bg-white rounded-lg shadow-sm overflow-hidden border">
          {filteredAndSortedData.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-gray-500 text-lg mb-2">No stocks found</div>
              <div className="text-gray-400 text-sm">Try adjusting your search criteria</div>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead style={{ backgroundColor: '#f2f3f7' }}>
                  <tr>
                    {columns.map(column => (
                      <th 
                        key={column} 
                        className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-200 transition-colors border-r border-gray-300 last:border-r-0"
                        onClick={() => handleSort(column)}
                      >
                        <div className="flex items-center">
                          {column}
                          {sortConfig?.key === column && (
                            <span className="ml-1 text-blue-500">
                              {sortConfig.direction === 'asc' ? '↑' : '↓'}
                            </span>
                          )}
                        </div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {currentData.map((row, index) => (
                    <tr 
                      key={row['S.No'] || index} 
                      className={index % 2 === 0 ? 'bg-white' : 'bg-[#9bec00]'}
                    >
                      {columns.map(column => (
                        <td key={column} className="px-4 py-3 text-sm text-gray-900 border-r border-gray-200 last:border-r-0">
                          {column === 'Name' ? (
                            <div className="font-medium text-blue-600 hover:text-blue-800 cursor-pointer">
                              {row[column]}
                            </div>
                          ) : typeof row[column] === 'number' && column !== 'S.No' ? (
                            <div className="text-right">
                              {column.includes('%') ? `${row[column]}%` : formatNumber(row[column])}
                            </div>
                          ) : (
                            row[column]
                          )}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-center space-x-2 mt-6">
            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
              let pageNum;
              if (totalPages <= 5) {
                pageNum = i + 1;
              } else if (currentPage <= 3) {
                pageNum = i + 1;
              } else if (currentPage >= totalPages - 2) {
                pageNum = totalPages - 4 + i;
              } else {
                pageNum = currentPage - 2 + i;
              }
              
              return (
                <button
                  key={pageNum}
                  onClick={() => handlePageChange(pageNum)}
                  className={`px-3 py-2 rounded font-medium transition-colors ${
                    currentPage === pageNum
                      ? 'bg-[#9bec00] text-black'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  {pageNum}
                </button>
              );
            })}
            {totalPages > 5 && currentPage < totalPages - 2 && (
              <>
                <span className="px-2 text-gray-500">...</span>
                <button
                  onClick={() => handlePageChange(totalPages)}
                  className="px-3 py-2 rounded font-medium bg-gray-200 text-gray-700 hover:bg-gray-300 transition-colors"
                >
                  {totalPages}
                </button>
              </>
            )}
            {currentPage < totalPages && (
              <button
                onClick={() => handlePageChange(currentPage + 1)}
                className="px-3 py-2 rounded font-medium bg-gray-200 text-gray-700 hover:bg-gray-300 transition-colors"
              >
                &gt;
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}