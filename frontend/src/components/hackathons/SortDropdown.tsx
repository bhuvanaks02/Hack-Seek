/**
 * Sort dropdown component for hackathons
 */
import React from 'react';

interface SortOption {
  label: string;
  value: string;
}

interface SortDropdownProps {
  value?: string;
  onChange: (value: string) => void;
  options?: SortOption[];
}

const SortDropdown: React.FC<SortDropdownProps> = ({
  value = 'relevance',
  onChange,
  options = [
    { label: 'Relevance', value: 'relevance' },
    { label: 'Newest First', value: 'newest' },
    { label: 'Start Date', value: 'start_date' },
    { label: 'Prize Money (High to Low)', value: 'prize_desc' },
    { label: 'Prize Money (Low to High)', value: 'prize_asc' },
    { label: 'Registration Deadline', value: 'deadline' },
    { label: 'Alphabetical', value: 'alphabetical' }
  ]
}) => {
  return (
    <div className="relative">
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="appearance-none bg-white border border-secondary-300 rounded-lg px-4 py-2 pr-8 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 cursor-pointer"
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            Sort by {option.label}
          </option>
        ))}
      </select>
      <div className="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none">
        <svg className="h-4 w-4 text-secondary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </div>
  );
};

export default SortDropdown;