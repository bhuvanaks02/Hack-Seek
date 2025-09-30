/**
 * Search filters component for hackathons
 */
import React from 'react';
import { Input, Button } from '../ui';
import { SearchFilters as SearchFiltersType } from '@/types';

interface SearchFiltersProps {
  filters: SearchFiltersType;
  onFiltersChange: (filters: SearchFiltersType) => void;
  onClearFilters: () => void;
}

const SearchFilters: React.FC<SearchFiltersProps> = ({
  filters,
  onFiltersChange,
  onClearFilters
}) => {
  const handleInputChange = (field: keyof SearchFiltersType, value: any) => {
    onFiltersChange({
      ...filters,
      [field]: value
    });
  };

  const handleCategoryToggle = (category: string) => {
    const categories = filters.categories || [];
    const updated = categories.includes(category)
      ? categories.filter(c => c !== category)
      : [...categories, category];

    handleInputChange('categories', updated);
  };

  const difficultyLevels = ['Beginner', 'Intermediate', 'Advanced', 'All'];
  const popularCategories = [
    'AI/ML', 'Web Development', 'Mobile', 'Blockchain', 'IoT', 'Gaming',
    'FinTech', 'HealthTech', 'Climate', 'Education', 'Data Science',
    'Cybersecurity', 'AR/VR', 'Social Impact', 'Hardware', 'DevOps'
  ];

  const dateRanges = [
    { label: 'This Week', value: 'this_week' },
    { label: 'This Month', value: 'this_month' },
    { label: 'Next 3 Months', value: 'next_3_months' },
    { label: 'This Year', value: 'this_year' }
  ];

  return (
    <div className="bg-white rounded-lg border border-secondary-200 p-6">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-medium text-secondary-900">Filters</h3>
        <Button
          variant="ghost"
          size="sm"
          onClick={onClearFilters}
          className="text-secondary-500 hover:text-secondary-700"
        >
          Clear All
        </Button>
      </div>

      <div className="space-y-6">
        {/* Search Query */}
        <div>
          <Input
            label="Search"
            placeholder="Search hackathons..."
            value={filters.q || ''}
            onChange={(e) => handleInputChange('q', e.target.value)}
            leftIcon={
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            }
          />
        </div>

        {/* Location */}
        <div>
          <Input
            label="Location"
            placeholder="City, Country or 'Online'"
            value={filters.location || ''}
            onChange={(e) => handleInputChange('location', e.target.value)}
            leftIcon={
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              </svg>
            }
          />
        </div>

        {/* Online Events */}
        <div>
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={filters.is_online || false}
              onChange={(e) => handleInputChange('is_online', e.target.checked)}
              className="h-4 w-4 text-primary-600 border-secondary-300 rounded focus:ring-primary-500"
            />
            <span className="ml-2 text-sm text-secondary-700">Online events only</span>
          </label>
        </div>

        {/* Difficulty Level */}
        <div>
          <label className="block text-sm font-medium text-secondary-700 mb-2">
            Difficulty Level
          </label>
          <div className="grid grid-cols-2 gap-2">
            {difficultyLevels.map((level) => (
              <label key={level} className="flex items-center">
                <input
                  type="radio"
                  name="difficulty"
                  value={level}
                  checked={filters.difficulty_level === level}
                  onChange={(e) => handleInputChange('difficulty_level', e.target.value)}
                  className="h-4 w-4 text-primary-600 border-secondary-300 focus:ring-primary-500"
                />
                <span className="ml-2 text-sm text-secondary-700">{level}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Prize Money */}
        <div>
          <Input
            label="Minimum Prize ($)"
            type="number"
            placeholder="0"
            value={filters.min_prize || ''}
            onChange={(e) => handleInputChange('min_prize', e.target.value ? parseFloat(e.target.value) : undefined)}
            leftIcon={
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
              </svg>
            }
          />
        </div>

        {/* Date Range */}
        <div>
          <label className="block text-sm font-medium text-secondary-700 mb-2">
            Date Range
          </label>
          <select
            value={filters.date_range || ''}
            onChange={(e) => handleInputChange('date_range', e.target.value || undefined)}
            className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="">Any time</option>
            {dateRanges.map((range) => (
              <option key={range.value} value={range.value}>
                {range.label}
              </option>
            ))}
          </select>
        </div>

        {/* Categories */}
        <div>
          <label className="block text-sm font-medium text-secondary-700 mb-3">
            Categories
          </label>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {popularCategories.map((category) => (
              <label key={category} className="flex items-center">
                <input
                  type="checkbox"
                  checked={(filters.categories || []).includes(category)}
                  onChange={() => handleCategoryToggle(category)}
                  className="h-4 w-4 text-primary-600 border-secondary-300 rounded focus:ring-primary-500"
                />
                <span className="ml-2 text-sm text-secondary-700">{category}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Apply Filters Button */}
        <div className="pt-4 border-t border-secondary-200">
          <Button
            className="w-full"
            onClick={() => {
              // Trigger search - this will be handled by parent component
            }}
          >
            Apply Filters
          </Button>
        </div>
      </div>
    </div>
  );
};

export default SearchFilters;