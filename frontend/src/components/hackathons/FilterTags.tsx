/**
 * Active filter tags component
 */
import React from 'react';
import { Badge } from '../ui';
import { SearchFilters } from '@/types';

interface FilterTagsProps {
  filters: SearchFilters;
  onRemoveFilter: (key: keyof SearchFilters, value?: string) => void;
  onClearAll: () => void;
}

const FilterTags: React.FC<FilterTagsProps> = ({
  filters,
  onRemoveFilter,
  onClearAll
}) => {
  const getActiveFilters = () => {
    const active: Array<{ key: keyof SearchFilters; label: string; value?: string }> = [];

    if (filters.q) {
      active.push({ key: 'q', label: `Search: "${filters.q}"` });
    }
    if (filters.location) {
      active.push({ key: 'location', label: `Location: ${filters.location}` });
    }
    if (filters.is_online) {
      active.push({ key: 'is_online', label: 'Online only' });
    }
    if (filters.difficulty_level && filters.difficulty_level !== 'All') {
      active.push({ key: 'difficulty_level', label: `Difficulty: ${filters.difficulty_level}` });
    }
    if (filters.min_prize && filters.min_prize > 0) {
      active.push({ key: 'min_prize', label: `Min Prize: $${filters.min_prize.toLocaleString()}` });
    }
    if (filters.categories && filters.categories.length > 0) {
      filters.categories.forEach(category => {
        active.push({ key: 'categories', label: category, value: category });
      });
    }

    return active;
  };

  const activeFilters = getActiveFilters();

  if (activeFilters.length === 0) {
    return null;
  }

  return (
    <div className="flex flex-wrap items-center gap-2 p-4 bg-secondary-50 rounded-lg border">
      <span className="text-sm text-secondary-600 font-medium">Active filters:</span>

      {activeFilters.map((filter, index) => (
        <Badge
          key={`${filter.key}-${filter.value || 'single'}-${index}`}
          variant="secondary"
          className="cursor-pointer hover:bg-secondary-200 transition-colors"
          onClick={() => onRemoveFilter(filter.key, filter.value)}
        >
          {filter.label}
          <svg className="ml-1 h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </Badge>
      ))}

      <button
        onClick={onClearAll}
        className="text-sm text-primary-600 hover:text-primary-700 font-medium ml-2"
      >
        Clear all
      </button>
    </div>
  );
};

export default FilterTags;