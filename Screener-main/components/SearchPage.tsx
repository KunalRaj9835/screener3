'use client';

import React from 'react';
import type { JSX } from 'react';
import { useState } from 'react';
import { ChevronDown, ChevronUp, Plus } from 'lucide-react';

// Type definitions
interface RatioData {
  displayName: string;
  hasPercent: boolean;
}

interface RatiosDataType {
  [key: string]: RatioData;
}

interface Filters {
  [key: string]: string;
}

type TabType = 'Create Screen' | 'Ready-made' | 'My Screens';
type CategoryType = 'Most Used' | 'Annual P&L' | 'Quarter P&L' | 'Balance Sheet' | 'Cash Flow' | 'Ratios' | 'Price';

const ratiosData: RatiosDataType = {
  'CMP Rs.': { displayName: 'CMP Rs.', hasPercent: false },
  'P/E': { displayName: 'P/E', hasPercent: false },
  'Mar Cap Rs.Cr': { displayName: 'Market Cap Rs.Cr', hasPercent: false },
  'Div Yld %': { displayName: 'Div Yld', hasPercent: true },
  'NP Qtr Rs.Cr': { displayName: 'NP Qtr Rs.Cr', hasPercent: false },
  'Qtr Profit Var %': { displayName: 'Qtr Profit Var', hasPercent: true },
  'Sales Qtr Rs.Cr': { displayName: 'Sales Qtr Rs.Cr', hasPercent: false },
  'Qtr Sales Var %': { displayName: 'Qtr Sales Var', hasPercent: true },
  'ROCE %': { displayName: 'ROCE', hasPercent: true },
  'ROE %': { displayName: 'ROE', hasPercent: true },
  'Debt to Equity': { displayName: 'Debt to Equity', hasPercent: false },
  'Current Ratio': { displayName: 'Current Ratio', hasPercent: false },
  'Quick Ratio': { displayName: 'Quick Ratio', hasPercent: false },
  'EPS Rs.': { displayName: 'EPS Rs.', hasPercent: false },
  'Book Value Rs.': { displayName: 'Book Value Rs.', hasPercent: false },
  'Sales Growth %': { displayName: 'Sales Growth', hasPercent: true },
  'Profit Growth %': { displayName: 'Profit Growth', hasPercent: true },
  'EBITDA Margin %': { displayName: 'EBITDA Margin', hasPercent: true }
};

const topRatios: string[] = ['CMP Rs.', 'P/E', 'Mar Cap Rs.Cr', 'Div Yld %'];

const symbols: string[] = ['+', '-', '*', '/', '>', '<', 'AND', 'OR'];

const categories: CategoryType[] = ['Most Used', 'Annual P&L', 'Quarter P&L', 'Balance Sheet', 'Cash Flow', 'Ratios', 'Price'];

const tabs: TabType[] = ['Create Screen', 'Ready-made', 'My Screens'];

export default function StockScreener() {
  const [activeTab, setActiveTab] = useState<TabType>('Create Screen');
  const [activeCategory, setActiveCategory] = useState<CategoryType>('Most Used');
  const [showRatios, setShowRatios] = useState<boolean>(false);
  const [showAllRatios, setShowAllRatios] = useState<boolean>(false);
  const [queryText, setQueryText] = useState("");
  const [query, setQuery] = useState<string>('');
  const [searchCompany, setSearchCompany] = useState<string>('');
  const [searchRatio, setSearchRatio] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [filters, setFilters] = useState<Filters>({});
  const [apiResults, setApiResults] = useState<any>(null);

  // Fixed API call function
  const sendExpressionQuery = async () => {
    if (!queryText.trim()) {
      alert('Please enter an expression to search');
      return;
    }

    setLoading(true);
    
    const payload = {
      timeframe: ["5min"], // could be made user-selectable
      filters: {
        expression: queryText
      },
      limit: 100
    };

    try {
      const res = await fetch("http://localhost:8001/api/v1/screen", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const data = await res.json();
      console.log("Query Result:", data);
      setApiResults(data);
      
      // Optionally navigate to results page with data
      // You can store the results in localStorage or pass via URL params
      // localStorage.setItem('queryResults', JSON.stringify(data));
      // window.location.href = '/query-result';
      
    } catch (err) {
      console.error("API error:", err);
      alert(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleRatioClick = (ratioKey: string): void => {
    const ratio: RatioData | undefined = ratiosData[ratioKey];
    if (!ratio) return;
    
    const ratioText: string = ratio.displayName;
    
    // Add to the queryText instead of searchCompany
    setQueryText(prev => prev + (prev ? ' AND ' : '') + ratioText + ' ');
  };

  const handleSymbolClick = (symbol: string): void => {
    setQueryText(prev => prev + symbol + ' ');
  };

  const isRatioQuery = (queryString: string): boolean => {
    const ratioNames = Object.values(ratiosData).map(ratio => ratio.displayName);
    return ratioNames.some(ratioName => queryString.includes(ratioName));
  };

  // This function now calls the API instead of just navigating
  const handleRunQuery = (): void => {
    sendExpressionQuery();
  };

  const handleSearch = (): void => {
    if (!queryText.trim()) {
      alert('Please enter a search query');
      return;
    }

    // For search button, you can either call API or navigate
    // Option 1: Call API
    sendExpressionQuery();
    
    // Option 2: Navigate (comment out above and uncomment below)
    /*
    setLoading(true);
    
    const searchParams = new URLSearchParams();
    const queryString = queryText.trim();
    
    if (isRatioQuery(queryString)) {
      searchParams.append('query', queryString);
    } else {
      searchParams.append('Name', queryString);
    }
    
    Object.keys(filters).forEach(key => {
      if (filters[key]) {
        searchParams.append(key, filters[key]);
      }
    });
    
    const resultUrl = `/query-result?${searchParams.toString()}`;
    window.location.href = resultUrl;
    */
  };

  const handleTabClick = (tab: TabType): void => {
    setActiveTab(tab);
  };

  const handleCategoryClick = (category: CategoryType): void => {
    setActiveCategory(category);
  };

  const handleQueryChange = (e: React.ChangeEvent<HTMLTextAreaElement>): void => {
    setQuery(e.target.value);
  };

  const handleSearchCompanyChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    setSearchCompany(e.target.value);
  };

  const handleSearchRatioChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    setSearchRatio(e.target.value);
  };

  const handleKeyPress = (e: React.KeyboardEvent): void => {
    if (e.key === 'Enter') {
      sendExpressionQuery();
    }
  };

  const toggleRatios = (): void => {
    setShowRatios(!showRatios);
  };

  const toggleAllRatios = (): void => {
    setShowAllRatios(true);
  };

  const renderContent = (): JSX.Element => {
    if (activeTab === 'Create Screen') {
      return (
        <div className="space-y-4">
          {/* Single Query Input */}
          <div className="relative">
            <input
              type="text"
              placeholder="Enter expression like: rsi_14 > 50 AND volume > volume_sma_20"
              value={queryText}
              onChange={(e) => setQueryText(e.target.value)}
              onKeyDown={handleKeyPress}
              className="w-full p-3 pr-12 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#9bec00]"
            />

            <button
              onClick={handleSearch}
              disabled={loading}
              className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-[#9bec00] hover:bg-[#8bd400] disabled:bg-gray-300 text-black p-2 rounded-lg transition-colors"
            >
              {loading ? (
                <div className="animate-spin h-4 w-4 border-2 border-black border-t-transparent rounded-full"></div>
              ) : (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              )}
            </button>
          </div>

          {/* Example Text */}
          <div className="text-gray-500 text-sm px-3">
            For example: Market capitalization &gt; 500 AND Price to earning &lt; 15 AND Return on capital employed &gt; 22%
          </div>

          {/* Run Query Button */}
          <button
            onClick={handleRunQuery}
            disabled={loading}
            className="bg-[#9bec00] hover:bg-[#8bd400] disabled:bg-gray-300 text-black font-medium px-6 py-2 rounded-lg transition-colors"
          >
            {loading ? 'Running Query...' : 'Run this query'}
          </button>

          {/* Display API Results */}
          {apiResults && (
            <div className="mt-4 p-4 bg-gray-50 rounded-lg">
              <h3 className="font-semibold mb-2">Query Results:</h3>
              <pre className="text-sm overflow-auto max-h-40">
                {JSON.stringify(apiResults, null, 2)}
              </pre>
            </div>
          )}

          {/* Clear Filters */}
          {(queryText || Object.keys(filters).some(key => filters[key])) && (
            <button
              onClick={() => {
                setQueryText('');
                setFilters({});
                setApiResults(null);
              }}
              className="w-full text-gray-500 hover:text-gray-700 py-2 text-sm transition-colors"
            >
              Clear all filters
            </button>
          )}
        </div>
      );
    } else {
      return (
        <div className="flex items-center justify-center h-32 text-gray-500">
          <p>Content for {activeTab} - Coming Soon</p>
        </div>
      );
    }
  };

  const filteredRatios = (): string[] => {
    if (!searchRatio) {
      return showAllRatios ? Object.keys(ratiosData) : topRatios;
    }
    
    return Object.keys(ratiosData).filter(ratioKey =>
      ratiosData[ratioKey].displayName.toLowerCase().includes(searchRatio.toLowerCase())
    );
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <div className="flex justify-between pl-10 pr-30 items-center px-8 py-4 border-b border-gray-200 ml-[10%]">
        <h1 className="text-2xl font-bold text-gray-800">Screener</h1>
        <button className="bg-[#9bec00] hover:bg-[#8bd400] text-black px-4 py-2 rounded-lg font-medium transition-colors">
          Demo Videos
        </button>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl pl-10 mx-auto p-6 ml-[10%] mr-[5%]">
        {/* Tabs */}
        <div className="flex space-x-1 mb-6 bg-gray-100 p-1 rounded-lg w-fit">
          {tabs.map((tab: TabType) => (
            <button
              key={tab}
              onClick={() => handleTabClick(tab)}
              className={`px-4 py-2 rounded-md font-medium transition-colors ${
                activeTab === tab
                  ? 'bg-[#9bec00] text-black'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Content Area */}
        <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
          {renderContent()}
        </div>

        {/* View Ratios Section */}
        <div className="bg-white border border-gray-200 rounded-lg">
          <button
            onClick={toggleRatios}
            className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-50 transition-colors"
          >
            <span className="text-gray-700">
              View ratios to get help in writing your query. 
              <span className="text-[#9bec00] ml-2 underline cursor-pointer">Show ratios</span>
            </span>
            <div className="flex items-center space-x-2">
              {showRatios ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
            </div>
          </button>

          {showRatios && (
            <div className="border-t border-gray-200 p-6 space-y-6">
              {/* Symbols */}
              <div>
                <h3 className="font-semibold text-gray-800 mb-3">Symbols</h3>
                <div className="flex flex-wrap gap-2">
                  {symbols.map((symbol: string) => (
                    <button
                      key={symbol}
                      onClick={() => handleSymbolClick(symbol)}
                      className="border border-gray-300 hover:border-[#9bec00] hover:bg-[#9bec00] hover:bg-opacity-10 px-3 py-2 rounded transition-colors"
                    >
                      {symbol}
                    </button>
                  ))}
                </div>
              </div>

              {/* Category Tabs */}
              <div>
                <div className="flex space-x-1 mb-4 bg-gray-100 p-1 rounded-lg w-fit">
                  {categories.map((category: CategoryType) => (
                    <button
                      key={category}
                      onClick={() => handleCategoryClick(category)}
                      className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                        category === activeCategory
                          ? 'bg-[#9bec00] text-black'
                          : 'text-gray-600 hover:text-gray-800'
                      }`}
                    >
                      {category}
                    </button>
                  ))}
                </div>

                {/* Search */}
                <div className="mb-4">
                  <div className="relative">
                    <input
                      type="text"
                      placeholder="Search ratio 'sales'"
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#9bec00] focus:border-transparent"
                      value={searchRatio}
                      onChange={handleSearchRatioChange}
                    />
                    <div className="absolute left-3 top-1/2 transform -translate-y-1/2">
                      <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                      </svg>
                    </div>
                  </div>
                </div>
              </div>

              {/* Recent */}
              <div>
                <h3 className="font-semibold text-gray-800 mb-3">Recent</h3>
                <div className="flex flex-wrap gap-2">
                  {filteredRatios().map((ratioKey: string) => (
                    <button
                      key={ratioKey}
                      onClick={() => handleRatioClick(ratioKey)}
                      className="border border-gray-300 hover:border-[#9bec00] hover:bg-[#9bec00] hover:bg-opacity-10 px-3 py-2 rounded text-sm transition-colors"
                    >
                      {ratiosData[ratioKey].displayName}
                    </button>
                  ))}
                  {!showAllRatios && !searchRatio && (
                    <button
                      onClick={toggleAllRatios}
                      className="border border-gray-300 hover:border-[#9bec00] hover:bg-[#9bec00] hover:bg-opacity-10 px-3 py-2 rounded text-sm transition-colors flex items-center"
                    >
                      <Plus className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>

              {/* Preceding */}
              <div>
                <h3 className="font-semibold text-gray-800 mb-3">Preceding</h3>
                <div className="flex flex-wrap gap-2">
                  {topRatios.map((ratioKey: string) => (
                    <button
                      key={ratioKey}
                      onClick={() => handleRatioClick(ratioKey)}
                      className="border border-gray-300 hover:border-[#9bec00] hover:bg-[#9bec00] hover:bg-opacity-10 px-3 py-2 rounded text-sm transition-colors"
                    >
                      {ratiosData[ratioKey].displayName}
                    </button>
                  ))}
                </div>
              </div>

              {/* Historical */}
              <div>
                <h3 className="font-semibold text-gray-800 mb-3">Historical</h3>
                <div className="flex flex-wrap gap-2">
                  {topRatios.map((ratioKey: string) => (
                    <button
                      key={ratioKey}
                      onClick={() => handleRatioClick(ratioKey)}
                      className="border border-gray-300 hover:border-[#9bec00] hover:bg-[#9bec00] hover:bg-opacity-10 px-3 py-2 rounded text-sm transition-colors"
                    >
                      {ratiosData[ratioKey].displayName}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}