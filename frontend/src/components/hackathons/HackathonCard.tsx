/**
 * Hackathon card component for displaying hackathon information
 */
import React from 'react';
import Link from 'next/link';
import { format } from 'date-fns';
import { Card, Badge } from '../ui';
import { Hackathon } from '@/types';

interface HackathonCardProps {
  hackathon: Hackathon;
  onFavorite?: (id: string) => void;
  isFavorited?: boolean;
}

const HackathonCard: React.FC<HackathonCardProps> = ({
  hackathon,
  onFavorite,
  isFavorited = false
}) => {
  const formatDate = (dateString?: string) => {
    if (!dateString) return null;
    try {
      return format(new Date(dateString), 'MMM dd, yyyy');
    } catch {
      return null;
    }
  };

  const getDifficultyColor = (level?: string) => {
    switch (level) {
      case 'Beginner': return 'success';
      case 'Intermediate': return 'warning';
      case 'Advanced': return 'error';
      default: return 'secondary';
    }
  };

  const isDeadlineSoon = () => {
    if (!hackathon.registration_deadline) return false;
    const deadline = new Date(hackathon.registration_deadline);
    const now = new Date();
    const diffDays = (deadline.getTime() - now.getTime()) / (1000 * 3600 * 24);
    return diffDays <= 7 && diffDays > 0;
  };

  return (
    <Card className="h-full hover:shadow-lg transition-shadow duration-200" padding="md">
      <div className="flex flex-col h-full">
        {/* Header */}
        <div className="flex justify-between items-start mb-3">
          <div className="flex-1">
            <Link href={`/hackathons/${hackathon.id}`}>
              <h3 className="text-lg font-semibold text-secondary-900 hover:text-primary-600 transition-colors line-clamp-2">
                {hackathon.title}
              </h3>
            </Link>
            {hackathon.organizer && (
              <p className="text-sm text-secondary-600 mt-1">by {hackathon.organizer}</p>
            )}
          </div>

          {/* Favorite button */}
          {onFavorite && (
            <button
              onClick={() => onFavorite(hackathon.id)}
              className={`p-2 rounded-full hover:bg-secondary-100 transition-colors ${
                isFavorited ? 'text-red-500' : 'text-secondary-400'
              }`}
            >
              <svg className="h-5 w-5" fill={isFavorited ? 'currentColor' : 'none'} viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </button>
          )}
        </div>

        {/* Description */}
        {hackathon.short_description && (
          <p className="text-sm text-secondary-600 mb-4 line-clamp-3 flex-grow">
            {hackathon.short_description}
          </p>
        )}

        {/* Badges */}
        <div className="flex flex-wrap gap-2 mb-4">
          {hackathon.is_online && (
            <Badge variant="primary" size="sm">Online</Badge>
          )}
          {hackathon.difficulty_level && (
            <Badge variant={getDifficultyColor(hackathon.difficulty_level)} size="sm">
              {hackathon.difficulty_level}
            </Badge>
          )}
          {hackathon.prize_money && hackathon.prize_money > 0 && (
            <Badge variant="success" size="sm">
              ${hackathon.prize_money.toLocaleString()}
            </Badge>
          )}
          {isDeadlineSoon() && (
            <Badge variant="warning" size="sm">
              Deadline Soon
            </Badge>
          )}
        </div>

        {/* Categories */}
        {hackathon.categories && hackathon.categories.length > 0 && (
          <div className="mb-4">
            <div className="flex flex-wrap gap-1">
              {hackathon.categories.slice(0, 3).map((category, index) => (
                <span
                  key={index}
                  className="px-2 py-1 text-xs bg-secondary-100 text-secondary-700 rounded"
                >
                  {category}
                </span>
              ))}
              {hackathon.categories.length > 3 && (
                <span className="px-2 py-1 text-xs bg-secondary-100 text-secondary-700 rounded">
                  +{hackathon.categories.length - 3} more
                </span>
              )}
            </div>
          </div>
        )}

        {/* Footer info */}
        <div className="mt-auto">
          <div className="flex justify-between items-center text-sm text-secondary-500">
            <div className="flex items-center space-x-4">
              {/* Location */}
              <div className="flex items-center">
                <svg className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                <span className="truncate max-w-24">
                  {hackathon.location || 'Location TBD'}
                </span>
              </div>

              {/* Date */}
              {hackathon.start_date && (
                <div className="flex items-center">
                  <svg className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  <span>{formatDate(hackathon.start_date)}</span>
                </div>
              )}
            </div>

            {/* Source */}
            {hackathon.source_platform && (
              <Badge variant="secondary" size="sm">
                {hackathon.source_platform}
              </Badge>
            )}
          </div>

          {/* Action button */}
          <div className="mt-3">
            <Link
              href={hackathon.registration_url || hackathon.website_url || '#'}
              target="_blank"
              rel="noopener noreferrer"
              className="w-full inline-flex justify-center items-center px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 transition-colors"
            >
              Register Now
              <svg className="ml-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </Link>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default HackathonCard;