/**
 * AI recommendation card component
 */
import React from 'react';
import Link from 'next/link';
import { format } from 'date-fns';
import { Card, Badge, Button } from '../ui';
import { Hackathon } from '@/types';

interface RecommendationData {
  hackathon: Hackathon;
  recommendation_score: number;
  reasons: string[];
}

interface RecommendationCardProps {
  recommendation: RecommendationData;
  onFavorite?: (id: string) => void;
  isFavorited?: boolean;
}

const RecommendationCard: React.FC<RecommendationCardProps> = ({
  recommendation,
  onFavorite,
  isFavorited = false
}) => {
  const { hackathon, recommendation_score, reasons } = recommendation;

  const formatDate = (dateString?: string) => {
    if (!dateString) return null;
    try {
      return format(new Date(dateString), 'MMM dd, yyyy');
    } catch {
      return null;
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600 bg-green-100';
    if (score >= 0.6) return 'text-yellow-600 bg-yellow-100';
    return 'text-orange-600 bg-orange-100';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 0.8) return 'Excellent Match';
    if (score >= 0.6) return 'Good Match';
    return 'Potential Match';
  };

  return (
    <Card className="h-full hover:shadow-lg transition-all duration-200 border-l-4 border-l-primary-500">
      <div className="flex flex-col h-full p-6">
        {/* Header with match score */}
        <div className="flex justify-between items-start mb-4">
          <div className="flex-1">
            <div className="flex items-center justify-between mb-2">
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getScoreColor(recommendation_score)}`}>
                <svg className="h-3 w-3 mr-1" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2L2 7v10c0 5.55 3.84 10 9 11 1.09-.87 2-1.92 2.71-3.08.4-.42.66-.96.85-1.54.14-.51.22-1.04.26-1.58.02-.37.03-.74.03-1.12V7l-10-5z"/>
                </svg>
                {getScoreLabel(recommendation_score)}
              </span>

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

            <Link href={`/hackathons/${hackathon.id}`}>
              <h3 className="text-lg font-semibold text-secondary-900 hover:text-primary-600 transition-colors line-clamp-2 mb-1">
                {hackathon.title}
              </h3>
            </Link>

            {hackathon.organizer && (
              <p className="text-sm text-secondary-600 mb-3">by {hackathon.organizer}</p>
            )}
          </div>
        </div>

        {/* AI Recommendation Reasons */}
        <div className="mb-4">
          <h4 className="text-sm font-medium text-secondary-900 mb-2 flex items-center">
            <svg className="h-4 w-4 mr-1 text-primary-600" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2L2 7v10c0 5.55 3.84 10 9 11 1.09-.87 2-1.92 2.71-3.08.4-.42.66-.96.85-1.54.14-.51.22-1.04.26-1.58.02-.37.03-.74.03-1.12V7l-10-5z"/>
            </svg>
            Why we recommend this:
          </h4>
          <ul className="space-y-1">
            {reasons.slice(0, 3).map((reason, index) => (
              <li key={index} className="flex items-start text-sm text-secondary-700">
                <svg className="h-3 w-3 mr-2 mt-1 text-primary-500" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                </svg>
                {reason}
              </li>
            ))}
          </ul>
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
            <Badge variant="secondary" size="sm">
              {hackathon.difficulty_level}
            </Badge>
          )}
          {hackathon.prize_money && hackathon.prize_money > 0 && (
            <Badge variant="success" size="sm">
              ${hackathon.prize_money.toLocaleString()}
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

        {/* Footer */}
        <div className="mt-auto">
          <div className="flex justify-between items-center text-sm text-secondary-500 mb-3">
            <div className="flex items-center space-x-4">
              <div className="flex items-center">
                <svg className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                </svg>
                <span className="truncate max-w-24">
                  {hackathon.location || 'Location TBD'}
                </span>
              </div>

              {hackathon.start_date && (
                <div className="flex items-center">
                  <svg className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  <span>{formatDate(hackathon.start_date)}</span>
                </div>
              )}
            </div>

            {hackathon.source_platform && (
              <Badge variant="secondary" size="sm">
                {hackathon.source_platform}
              </Badge>
            )}
          </div>

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
    </Card>
  );
};

export default RecommendationCard;