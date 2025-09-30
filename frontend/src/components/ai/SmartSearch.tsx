/**
 * AI-powered smart search component
 */
import React, { useState } from 'react';
import { Button, Input } from '../ui';

interface SmartSearchProps {
  onSearch: (query: string, options: { semantic: boolean }) => void;
  loading?: boolean;
  placeholder?: string;
}

const SmartSearch: React.FC<SmartSearchProps> = ({
  onSearch,
  loading = false,
  placeholder = "Try: 'AI hackathons with good prizes for beginners'"
}) => {
  const [query, setQuery] = useState('');
  const [useAI, setUseAI] = useState(true);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim(), { semantic: useAI });
    }
  };

  const quickSearches = [
    "AI hackathons with prizes over $10k",
    "Web development competitions for beginners",
    "Online blockchain hackathons this month",
    "Mobile app contests with React Native",
    "Climate tech challenges for students"
  ];

  const handleQuickSearch = (quickQuery: string) => {
    setQuery(quickQuery);
    onSearch(quickQuery, { semantic: useAI });
  };

  return (
    <div className="space-y-4">
      <form onSubmit={handleSubmit} className="space-y-3">
        <div className="relative">
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={placeholder}
            disabled={loading}
            className="pr-24"
            leftIcon={
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            }
          />

          {/* AI Toggle */}
          <div className="absolute right-2 top-1/2 transform -translate-y-1/2">
            <button
              type="button"
              onClick={() => setUseAI(!useAI)}
              className={`px-2 py-1 text-xs rounded-full transition-colors ${
                useAI
                  ? 'bg-primary-100 text-primary-700 border border-primary-300'
                  : 'bg-secondary-100 text-secondary-600 border border-secondary-300'
              }`}
              title={useAI ? "AI search enabled" : "Basic search"}
            >
              {useAI ? (
                <div className="flex items-center space-x-1">
                  <svg className="h-3 w-3" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2L2 7v10c0 5.55 3.84 10 9 11 1.09-.87 2-1.92 2.71-3.08.4-.42.66-.96.85-1.54.14-.51.22-1.04.26-1.58.02-.37.03-.74.03-1.12V7l-10-5z"/>
                  </svg>
                  <span>AI</span>
                </div>
              ) : (
                'Basic'
              )}
            </button>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="use-ai"
              checked={useAI}
              onChange={(e) => setUseAI(e.target.checked)}
              className="h-4 w-4 text-primary-600 border-secondary-300 rounded focus:ring-primary-500"
            />
            <label htmlFor="use-ai" className="text-sm text-secondary-700">
              Use AI-powered semantic search
            </label>
          </div>

          <Button
            type="submit"
            disabled={loading || !query.trim()}
            loading={loading}
            size="sm"
          >
            {loading ? 'Searching...' : 'Search'}
          </Button>
        </div>
      </form>

      {/* Quick search suggestions */}
      <div className="space-y-2">
        <p className="text-sm font-medium text-secondary-700">Try these searches:</p>
        <div className="flex flex-wrap gap-2">
          {quickSearches.map((quickQuery, index) => (
            <button
              key={index}
              onClick={() => handleQuickSearch(quickQuery)}
              className="px-3 py-1 text-sm bg-secondary-100 text-secondary-700 rounded-full hover:bg-secondary-200 transition-colors"
              disabled={loading}
            >
              {quickQuery}
            </button>
          ))}
        </div>
      </div>

      {useAI && (
        <div className="bg-primary-50 border border-primary-200 rounded-lg p-3">
          <div className="flex items-start space-x-2">
            <svg className="h-5 w-5 text-primary-600 mt-0.5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2L2 7v10c0 5.55 3.84 10 9 11 1.09-.87 2-1.92 2.71-3.08.4-.42.66-.96.85-1.54.14-.51.22-1.04.26-1.58.02-.37.03-.74.03-1.12V7l-10-5z"/>
            </svg>
            <div>
              <h4 className="text-sm font-medium text-primary-800">AI Search Active</h4>
              <p className="text-sm text-primary-700">
                Use natural language to describe what you're looking for.
                AI will understand context and find the most relevant hackathons.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SmartSearch;