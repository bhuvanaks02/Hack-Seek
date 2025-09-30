/**
 * Mobile filters modal component
 */
import React, { useEffect } from 'react';
import { Button } from '../ui';
import SearchFilters from './SearchFilters';
import { SearchFilters as SearchFiltersType } from '@/types';

interface MobileFiltersProps {
  isOpen: boolean;
  onClose: () => void;
  filters: SearchFiltersType;
  onFiltersChange: (filters: SearchFiltersType) => void;
  onClearFilters: () => void;
  resultsCount: number;
}

const MobileFilters: React.FC<MobileFiltersProps> = ({
  isOpen,
  onClose,
  filters,
  onFiltersChange,
  onClearFilters,
  resultsCount
}) => {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 lg:hidden">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="fixed inset-y-0 right-0 w-full max-w-sm bg-white shadow-xl overflow-y-auto">
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-secondary-200">
            <h2 className="text-lg font-medium text-secondary-900">Filters</h2>
            <button
              onClick={onClose}
              className="p-2 rounded-lg hover:bg-secondary-100 transition-colors"
            >
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Filters content */}
          <div className="flex-1 p-4">
            <SearchFilters
              filters={filters}
              onFiltersChange={onFiltersChange}
              onClearFilters={onClearFilters}
            />
          </div>

          {/* Footer */}
          <div className="border-t border-secondary-200 p-4 space-y-3">
            <div className="text-sm text-secondary-600 text-center">
              {resultsCount.toLocaleString()} hackathons found
            </div>
            <Button
              className="w-full"
              onClick={onClose}
            >
              Show Results
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MobileFilters;