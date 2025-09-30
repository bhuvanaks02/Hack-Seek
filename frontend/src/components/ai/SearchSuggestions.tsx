/**
 * Intelligent search suggestions component
 */
import React, { useState, useEffect, useRef } from 'react';

interface SearchSuggestionsProps {
  query: string;
  onSuggestionSelect: (suggestion: string) => void;
  isVisible: boolean;
  onClose: () => void;
}

interface Suggestion {
  text: string;
  type: 'recent' | 'popular' | 'ai' | 'category' | 'technology';
  score?: number;
}

const SearchSuggestions: React.FC<SearchSuggestionsProps> = ({
  query,
  onSuggestionSelect,
  isVisible,
  onClose
}) => {
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [loading, setLoading] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isVisible && query.length >= 2) {
      fetchSuggestions();
    } else {
      setSuggestions([]);
    }
  }, [query, isVisible]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        onClose();
      }
    };

    if (isVisible) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isVisible, onClose]);

  const fetchSuggestions = async () => {
    try {
      setLoading(true);

      // Combine different types of suggestions
      const allSuggestions: Suggestion[] = [
        ...getLocalSuggestions(query),
        ...await getAISuggestions(query)
      ];

      // Remove duplicates and sort by relevance
      const uniqueSuggestions = Array.from(
        new Map(allSuggestions.map(s => [s.text.toLowerCase(), s])).values()
      );

      setSuggestions(uniqueSuggestions.slice(0, 8));

    } catch (error) {
      console.error('Error fetching suggestions:', error);
      setSuggestions(getLocalSuggestions(query));
    } finally {
      setLoading(false);
    }
  };

  const getLocalSuggestions = (searchQuery: string): Suggestion[] => {
    const queryLower = searchQuery.toLowerCase();

    // Popular categories and technologies
    const categories = [
      'AI/ML hackathons', 'Web development contests', 'Mobile app challenges',
      'Blockchain events', 'FinTech competitions', 'HealthTech hackathons',
      'Climate tech challenges', 'Gaming contests', 'IoT hackathons'
    ];

    const technologies = [
      'React hackathons', 'Python competitions', 'Node.js events',
      'Flutter challenges', 'TensorFlow contests', 'Unity hackathons',
      'AWS cloud hackathons', 'Docker competitions'
    ];

    const popularQueries = [
      'hackathons with high prizes', 'beginner-friendly competitions',
      'online hackathons this month', 'student hackathons',
      'weekend coding contests', 'startup pitch competitions',
      'open source hackathons', 'women in tech events'
    ];

    const allOptions = [
      ...categories.map(c => ({ text: c, type: 'category' as const })),
      ...technologies.map(t => ({ text: t, type: 'technology' as const })),
      ...popularQueries.map(q => ({ text: q, type: 'popular' as const }))
    ];

    // Filter based on query
    return allOptions
      .filter(option => option.text.toLowerCase().includes(queryLower))
      .slice(0, 5);
  };

  const getAISuggestions = async (searchQuery: string): Promise<Suggestion[]> => {
    try {
      // Simulate AI suggestion generation
      const aiSuggestions = generateAISuggestions(searchQuery);
      return aiSuggestions.map(text => ({ text, type: 'ai' as const, score: 0.8 }));
    } catch (error) {
      return [];
    }
  };

  const generateAISuggestions = (searchQuery: string): string[] => {
    const queryLower = searchQuery.toLowerCase();

    // AI-powered query expansion based on context
    const expansions: { [key: string]: string[] } = {
      'ai': [
        'AI hackathons with machine learning focus',
        'artificial intelligence competitions for beginners',
        'AI startup challenges with mentorship'
      ],
      'web': [
        'web development hackathons with React',
        'full-stack web competitions',
        'frontend development challenges'
      ],
      'mobile': [
        'mobile app development contests',
        'iOS and Android hackathons',
        'cross-platform mobile challenges'
      ],
      'blockchain': [
        'blockchain hackathons with crypto prizes',
        'DeFi development competitions',
        'Web3 startup challenges'
      ],
      'beginner': [
        'beginner-friendly hackathons with tutorials',
        'first-time hackathon experiences',
        'coding bootcamp graduate competitions'
      ],
      'student': [
        'university hackathons for students',
        'student-only coding competitions',
        'college hackathon events'
      ],
      'prize': [
        'high-prize hackathons over $10k',
        'cash prize coding competitions',
        'sponsored hackathons with awards'
      ]
    };

    // Find relevant expansions
    const relevantExpansions: string[] = [];

    Object.entries(expansions).forEach(([keyword, suggestions]) => {
      if (queryLower.includes(keyword)) {
        relevantExpansions.push(...suggestions);
      }
    });

    // If no specific expansions found, provide general smart suggestions
    if (relevantExpansions.length === 0) {
      return [
        `${searchQuery} hackathons with good prizes`,
        `${searchQuery} competitions for developers`,
        `online ${searchQuery} coding contests`
      ];
    }

    return relevantExpansions.slice(0, 3);
  };

  const getSuggestionIcon = (type: string) => {
    switch (type) {
      case 'ai':
        return (
          <svg className="h-4 w-4 text-primary-600" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2L2 7v10c0 5.55 3.84 10 9 11 1.09-.87 2-1.92 2.71-3.08.4-.42.66-.96.85-1.54.14-.51.22-1.04.26-1.58.02-.37.03-.74.03-1.12V7l-10-5z"/>
          </svg>
        );
      case 'popular':
        return (
          <svg className="h-4 w-4 text-orange-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        );
      case 'category':
        return (
          <svg className="h-4 w-4 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
          </svg>
        );
      case 'technology':
        return (
          <svg className="h-4 w-4 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
          </svg>
        );
      default:
        return (
          <svg className="h-4 w-4 text-secondary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        );
    }
  };

  const getSuggestionLabel = (type: string) => {
    switch (type) {
      case 'ai':
        return 'AI Suggestion';
      case 'popular':
        return 'Popular';
      case 'category':
        return 'Category';
      case 'technology':
        return 'Technology';
      case 'recent':
        return 'Recent';
      default:
        return '';
    }
  };

  if (!isVisible || suggestions.length === 0) {
    return null;
  }

  return (
    <div
      ref={containerRef}
      className="absolute top-full left-0 right-0 mt-1 bg-white border border-secondary-200 rounded-lg shadow-lg z-50 max-h-80 overflow-y-auto"
    >
      {loading && (
        <div className="p-3 text-center">
          <div className="inline-flex items-center text-sm text-secondary-500">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-600 mr-2"></div>
            Loading suggestions...
          </div>
        </div>
      )}

      {!loading && (
        <div className="py-2">
          {suggestions.map((suggestion, index) => (
            <button
              key={index}
              onClick={() => onSuggestionSelect(suggestion.text)}
              className="w-full px-4 py-2 text-left hover:bg-secondary-50 transition-colors group"
            >
              <div className="flex items-center space-x-3">
                <div className="flex-shrink-0">
                  {getSuggestionIcon(suggestion.type)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-secondary-900 group-hover:text-primary-600 transition-colors truncate">
                    {suggestion.text}
                  </p>
                  {getSuggestionLabel(suggestion.type) && (
                    <p className="text-xs text-secondary-500">
                      {getSuggestionLabel(suggestion.type)}
                      {suggestion.score && (
                        <span className="ml-2 text-primary-600">
                          {Math.round(suggestion.score * 100)}% match
                        </span>
                      )}
                    </p>
                  )}
                </div>
                <div className="flex-shrink-0">
                  <svg className="h-4 w-4 text-secondary-400 group-hover:text-primary-600 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </div>
            </button>
          ))}

          {/* Footer */}
          <div className="border-t border-secondary-200 px-4 py-2 bg-secondary-50">
            <p className="text-xs text-secondary-500 flex items-center">
              <svg className="h-3 w-3 mr-1 text-primary-600" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2L2 7v10c0 5.55 3.84 10 9 11 1.09-.87 2-1.92 2.71-3.08.4-.42.66-.96.85-1.54.14-.51.22-1.04.26-1.58.02-.37.03-.74.03-1.12V7l-10-5z"/>
              </svg>
              AI-powered suggestions
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default SearchSuggestions;