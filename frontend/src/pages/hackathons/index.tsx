/**
 * Main hackathons listing page
 */
import React, { useState, useEffect } from 'react';
import { GetServerSideProps } from 'next';
import { useRouter } from 'next/router';
import Layout from '@/components/layout/Layout';
import HackathonCard from '@/components/hackathons/HackathonCard';
import SearchFilters from '@/components/hackathons/SearchFilters';
import SortDropdown from '@/components/hackathons/SortDropdown';
import FilterTags from '@/components/hackathons/FilterTags';
import MobileFilters from '@/components/hackathons/MobileFilters';
import SmartSearch from '@/components/ai/SmartSearch';
import { Button, Input } from '@/components/ui';
import { Hackathon, SearchFilters as SearchFiltersType, PaginatedResponse } from '@/types';

interface HackathonsPageProps {
  initialData?: PaginatedResponse<Hackathon>;
  initialFilters?: SearchFiltersType;
}

const HackathonsPage: React.FC<HackathonsPageProps> = ({
  initialData,
  initialFilters = {}
}) => {
  const router = useRouter();
  const [hackathons, setHackathons] = useState<Hackathon[]>(initialData?.data || []);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<SearchFiltersType>(initialFilters);
  const [pagination, setPagination] = useState({
    total: initialData?.total || 0,
    page: initialData?.page || 1,
    pages: initialData?.pages || 1,
    size: initialData?.size || 12
  });
  const [favorites, setFavorites] = useState<string[]>([]);
  const [showMobileFilters, setShowMobileFilters] = useState(false);
  const [showSmartSearch, setShowSmartSearch] = useState(false);
  const [aiSearchResults, setAiSearchResults] = useState<any>(null);

  const fetchHackathons = async (newFilters: SearchFiltersType, page = 1) => {
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams();

      if (newFilters.q) params.set('q', newFilters.q);
      if (newFilters.location) params.set('location', newFilters.location);
      if (newFilters.is_online) params.set('is_online', 'true');
      if (newFilters.difficulty_level) params.set('difficulty_level', newFilters.difficulty_level);
      if (newFilters.min_prize) params.set('min_prize', newFilters.min_prize.toString());
      if (newFilters.categories?.length) params.set('categories', newFilters.categories.join(','));

      params.set('page', page.toString());
      params.set('size', pagination.size.toString());

      const response = await fetch(`/api/hackathons?${params.toString()}`);
      if (!response.ok) throw new Error('Failed to fetch hackathons');

      const data: PaginatedResponse<Hackathon> = await response.json();

      setHackathons(data.data);
      setPagination({
        total: data.total,
        page: data.page,
        pages: data.pages,
        size: data.size
      });

      // Update URL without page reload
      const queryParams = new URLSearchParams();
      Object.entries(newFilters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          if (Array.isArray(value)) {
            if (value.length > 0) queryParams.set(key, value.join(','));
          } else {
            queryParams.set(key, value.toString());
          }
        }
      });
      if (page > 1) queryParams.set('page', page.toString());

      const newUrl = queryParams.toString()
        ? `/hackathons?${queryParams.toString()}`
        : '/hackathons';

      router.replace(newUrl, undefined, { shallow: true });

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleFiltersChange = (newFilters: SearchFiltersType) => {
    setFilters(newFilters);
    fetchHackathons(newFilters, 1);
  };

  const handleClearFilters = () => {
    const clearedFilters: SearchFiltersType = {};
    setFilters(clearedFilters);
    setSearchQuery('');
    fetchHackathons(clearedFilters, 1);
  };

  const handleRemoveFilter = (key: keyof SearchFiltersType, value?: string) => {
    const newFilters = { ...filters };

    if (key === 'categories' && value && newFilters.categories) {
      newFilters.categories = newFilters.categories.filter(c => c !== value);
      if (newFilters.categories.length === 0) {
        delete newFilters.categories;
      }
    } else {
      delete newFilters[key];
      if (key === 'q') {
        setSearchQuery('');
      }
    }

    setFilters(newFilters);
    fetchHackathons(newFilters, 1);
  };

  const handlePageChange = (newPage: number) => {
    fetchHackathons(filters, newPage);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleFavorite = async (hackathonId: string) => {
    try {
      const isFavorited = favorites.includes(hackathonId);

      if (isFavorited) {
        setFavorites(prev => prev.filter(id => id !== hackathonId));
        // API call to remove favorite
      } else {
        setFavorites(prev => [...prev, hackathonId]);
        // API call to add favorite
      }
    } catch (err) {
      console.error('Failed to update favorite:', err);
    }
  };

  const handleSmartSearch = async (query: string, options: { semantic: boolean }) => {
    setLoading(true);
    setError(null);
    setAiSearchResults(null);

    try {
      const endpoint = options.semantic ? '/api/hackathons/ai/search' : '/api/hackathons/search';
      const params = new URLSearchParams();

      if (options.semantic) {
        params.set('query', query);
        params.set('limit', '20');
      } else {
        params.set('q', query);
        params.set('semantic', 'false');
        params.set('page', '1');
        params.set('size', '20');
      }

      const response = await fetch(`${endpoint}?${params.toString()}`);
      if (!response.ok) throw new Error('Search failed');

      const data = await response.json();

      if (options.semantic) {
        setAiSearchResults(data);
        setHackathons(data.results.map((r: any) => r.hackathon));
        setPagination({
          total: data.total_results,
          page: 1,
          pages: 1,
          size: data.total_results
        });
      } else {
        setHackathons(data.data);
        setPagination({
          total: data.total,
          page: data.page,
          pages: data.pages,
          size: data.size
        });
      }

      // Update filters to show the search query
      setFilters({ ...filters, q: query });
      setSearchQuery(query);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
    } finally {
      setLoading(false);
    }
  };

  // Search input with debounce
  const [searchQuery, setSearchQuery] = useState(filters.q || '');

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (searchQuery !== filters.q) {
        handleFiltersChange({ ...filters, q: searchQuery });
      }
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [searchQuery]);

  const sortOptions = [
    { label: 'Relevance', value: 'relevance' },
    { label: 'Newest First', value: 'newest' },
    { label: 'Start Date', value: 'start_date' },
    { label: 'Prize Money', value: 'prize_desc' },
    { label: 'Registration Deadline', value: 'deadline' }
  ];

  return (
    <Layout
      title="Find Hackathons - HackSeek"
      description="Discover hackathons worldwide. Filter by location, technology, prize money, and difficulty level."
    >
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between">
            <div>
              <h1 className="text-3xl font-bold text-secondary-900">Find Hackathons</h1>
              <p className="mt-2 text-secondary-600">
                Discover {pagination.total.toLocaleString()} hackathons worldwide
              </p>
            </div>

            {/* Search options */}
            <div className="mt-4 md:mt-0 flex items-center space-x-3">
              <div className="flex border border-secondary-300 rounded-lg">
                <button
                  onClick={() => setShowSmartSearch(false)}
                  className={`px-3 py-2 text-sm font-medium rounded-l-lg ${
                    !showSmartSearch
                      ? 'bg-primary-600 text-white'
                      : 'text-secondary-700 hover:bg-secondary-50'
                  }`}
                >
                  Basic
                </button>
                <button
                  onClick={() => setShowSmartSearch(true)}
                  className={`px-3 py-2 text-sm font-medium rounded-r-lg ${
                    showSmartSearch
                      ? 'bg-primary-600 text-white'
                      : 'text-secondary-700 hover:bg-secondary-50'
                  }`}
                >
                  <svg className="h-4 w-4 mr-1 inline" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2L2 7v10c0 5.55 3.84 10 9 11 1.09-.87 2-1.92 2.71-3.08.4-.42.66-.96.85-1.54.14-.51.22-1.04.26-1.58.02-.37.03-.74.03-1.12V7l-10-5z"/>
                  </svg>
                  AI Search
                </button>
              </div>

              {!showSmartSearch && (
                <div className="md:w-80">
                  <Input
                    placeholder="Search hackathons..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    leftIcon={
                      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                      </svg>
                    }
                  />
                </div>
              )}
            </div>
          </div>

          {/* Smart Search Section */}
          {showSmartSearch && (
            <div className="mt-6 border-t border-secondary-200 pt-6">
              <SmartSearch
                onSearch={handleSmartSearch}
                loading={loading}
              />

              {/* AI Search Results Info */}
              {aiSearchResults && (
                <div className="mt-4 bg-primary-50 border border-primary-200 rounded-lg p-4">
                  <div className="flex items-start space-x-3">
                    <svg className="h-5 w-5 text-primary-600 mt-0.5" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 2L2 7v10c0 5.55 3.84 10 9 11 1.09-.87 2-1.92 2.71-3.08.4-.42.66-.96.85-1.54.14-.51.22-1.04.26-1.58.02-.37.03-.74.03-1.12V7l-10-5z"/>
                    </svg>
                    <div className="flex-1">
                      <h4 className="text-sm font-medium text-primary-800">
                        AI Search Results for "{aiSearchResults.query}"
                      </h4>
                      <p className="text-sm text-primary-700 mt-1">
                        Processed query: "{aiSearchResults.processed_query}"
                      </p>
                      {Object.keys(aiSearchResults.extracted_filters || {}).length > 0 && (
                        <div className="mt-2">
                          <p className="text-sm text-primary-700">
                            Extracted filters: {JSON.stringify(aiSearchResults.extracted_filters)}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="lg:grid lg:grid-cols-4 lg:gap-8">
          {/* Filters sidebar - hidden on mobile */}
          <div className="hidden lg:block lg:col-span-1">
            <div className="sticky top-4">
              <SearchFilters
                filters={filters}
                onFiltersChange={handleFiltersChange}
                onClearFilters={handleClearFilters}
              />
            </div>
          </div>

          {/* Main content */}
          <div className="lg:col-span-3">
            {/* Mobile filter button */}
            <div className="lg:hidden mb-4">
              <Button
                variant="ghost"
                onClick={() => setShowMobileFilters(true)}
                className="w-full justify-center"
              >
                <svg className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.707A1 1 0 013 7V4z" />
                </svg>
                Filters {Object.keys(filters).length > 0 && `(${Object.keys(filters).length})`}
              </Button>
            </div>

            {/* Active filters */}
            <div className="mb-6">
              <FilterTags
                filters={filters}
                onRemoveFilter={handleRemoveFilter}
                onClearAll={handleClearFilters}
              />
            </div>

            {/* Results header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6">
              <div className="flex items-center space-x-4">
                <p className="text-sm text-secondary-600">
                  Showing {((pagination.page - 1) * pagination.size) + 1}-{Math.min(pagination.page * pagination.size, pagination.total)} of {pagination.total} results
                </p>
                {loading && (
                  <div className="flex items-center text-sm text-secondary-500">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-600 mr-2"></div>
                    Loading...
                  </div>
                )}
              </div>

              {/* Sort dropdown */}
              <div className="mt-4 sm:mt-0">
                <SortDropdown
                  value={filters.sort}
                  onChange={(value) => handleFiltersChange({ ...filters, sort: value })}
                />
              </div>
            </div>

            {/* Error state */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                <div className="flex">
                  <svg className="h-5 w-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div className="ml-3">
                    <p className="text-sm text-red-800">{error}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Hackathons grid */}
            {hackathons.length > 0 ? (
              <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-6 mb-8">
                {hackathons.map((hackathon) => (
                  <HackathonCard
                    key={hackathon.id}
                    hackathon={hackathon}
                    onFavorite={handleFavorite}
                    isFavorited={favorites.includes(hackathon.id)}
                  />
                ))}
              </div>
            ) : !loading && (
              <div className="text-center py-12">
                <svg className="mx-auto h-12 w-12 text-secondary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <h3 className="mt-2 text-sm font-medium text-secondary-900">No hackathons found</h3>
                <p className="mt-1 text-sm text-secondary-500">
                  Try adjusting your search filters to find more results.
                </p>
                <div className="mt-6">
                  <Button onClick={handleClearFilters}>
                    Clear all filters
                  </Button>
                </div>
              </div>
            )}

            {/* Pagination */}
            {pagination.pages > 1 && (
              <div className="flex items-center justify-between border-t border-secondary-200 bg-white px-4 py-3 sm:px-6">
                <div className="flex flex-1 justify-between sm:hidden">
                  <Button
                    variant="ghost"
                    onClick={() => handlePageChange(pagination.page - 1)}
                    disabled={pagination.page <= 1}
                  >
                    Previous
                  </Button>
                  <Button
                    variant="ghost"
                    onClick={() => handlePageChange(pagination.page + 1)}
                    disabled={pagination.page >= pagination.pages}
                  >
                    Next
                  </Button>
                </div>
                <div className="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
                  <div>
                    <p className="text-sm text-secondary-700">
                      Page <span className="font-medium">{pagination.page}</span> of{' '}
                      <span className="font-medium">{pagination.pages}</span>
                    </p>
                  </div>
                  <div>
                    <nav className="isolate inline-flex -space-x-px rounded-md shadow-sm">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handlePageChange(pagination.page - 1)}
                        disabled={pagination.page <= 1}
                        className="rounded-r-none"
                      >
                        Previous
                      </Button>

                      {/* Page numbers */}
                      {Array.from({ length: Math.min(5, pagination.pages) }, (_, i) => {
                        const page = Math.max(1, Math.min(pagination.pages - 4, pagination.page - 2)) + i;
                        return (
                          <Button
                            key={page}
                            variant={page === pagination.page ? "primary" : "ghost"}
                            size="sm"
                            onClick={() => handlePageChange(page)}
                            className="rounded-none"
                          >
                            {page}
                          </Button>
                        );
                      })}

                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handlePageChange(pagination.page + 1)}
                        disabled={pagination.page >= pagination.pages}
                        className="rounded-l-none"
                      >
                        Next
                      </Button>
                    </nav>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Mobile Filters Modal */}
        <MobileFilters
          isOpen={showMobileFilters}
          onClose={() => setShowMobileFilters(false)}
          filters={filters}
          onFiltersChange={handleFiltersChange}
          onClearFilters={handleClearFilters}
          resultsCount={pagination.total}
        />
      </div>
    </Layout>
  );
};

export const getServerSideProps: GetServerSideProps = async (context) => {
  const { query } = context;

  try {
    const params = new URLSearchParams();

    // Extract filters from query parameters
    const filters: SearchFiltersType = {};

    if (query.q) {
      filters.q = query.q as string;
      params.set('q', filters.q);
    }
    if (query.location) {
      filters.location = query.location as string;
      params.set('location', filters.location);
    }
    if (query.is_online === 'true') {
      filters.is_online = true;
      params.set('is_online', 'true');
    }
    if (query.difficulty_level) {
      filters.difficulty_level = query.difficulty_level as string;
      params.set('difficulty_level', filters.difficulty_level);
    }
    if (query.min_prize) {
      filters.min_prize = parseFloat(query.min_prize as string);
      params.set('min_prize', filters.min_prize.toString());
    }
    if (query.categories) {
      filters.categories = (query.categories as string).split(',');
      params.set('categories', filters.categories.join(','));
    }

    const page = parseInt(query.page as string) || 1;
    params.set('page', page.toString());
    params.set('size', '12');

    // Fetch data from API
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/hackathons?${params.toString()}`);

    if (!response.ok) {
      throw new Error('Failed to fetch hackathons');
    }

    const data: PaginatedResponse<Hackathon> = await response.json();

    return {
      props: {
        initialData: data,
        initialFilters: filters
      }
    };
  } catch (error) {
    console.error('Error fetching hackathons:', error);

    // Return empty data on error
    return {
      props: {
        initialData: {
          data: [],
          total: 0,
          page: 1,
          pages: 1,
          size: 12
        },
        initialFilters: {}
      }
    };
  }
};

export default HackathonsPage;