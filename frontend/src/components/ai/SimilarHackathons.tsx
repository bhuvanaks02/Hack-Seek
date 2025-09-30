/**
 * Similar hackathons component using AI
 */
import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Card, Badge, Button } from '../ui';
import { Hackathon } from '@/types';

interface SimilarHackathonsProps {
  hackathonId: string;
  currentTitle?: string;
}

const SimilarHackathons: React.FC<SimilarHackathonsProps> = ({
  hackathonId,
  currentTitle = 'this hackathon'
}) => {
  const [similarHackathons, setSimilarHackathons] = useState<Hackathon[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchSimilarHackathons();
  }, [hackathonId]);

  const fetchSimilarHackathons = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`/api/hackathons/ai/similar/${hackathonId}?limit=5`);

      if (!response.ok) {
        throw new Error('Failed to fetch similar hackathons');
      }

      const data = await response.json();
      setSimilarHackathons(data);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-secondary-900 mb-4 flex items-center">
          <svg className="h-5 w-5 mr-2 text-primary-600" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2L2 7v10c0 5.55 3.84 10 9 11 1.09-.87 2-1.92 2.71-3.08.4-.42.66-.96.85-1.54.14-.51.22-1.04.26-1.58.02-.37.03-.74.03-1.12V7l-10-5z"/>
          </svg>
          Similar Hackathons
        </h3>
        <div className="space-y-4">
          {[...Array(3)].map((_, index) => (
            <div key={index} className="animate-pulse">
              <div className="h-4 bg-secondary-200 rounded w-3/4 mb-2"></div>
              <div className="h-3 bg-secondary-200 rounded w-1/2 mb-2"></div>
              <div className="flex space-x-2">
                <div className="h-6 bg-secondary-200 rounded w-16"></div>
                <div className="h-6 bg-secondary-200 rounded w-20"></div>
              </div>
            </div>
          ))}
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-secondary-900 mb-4">Similar Hackathons</h3>
        <div className="text-center py-4">
          <p className="text-sm text-secondary-500">Unable to load similar hackathons</p>
          <Button variant="ghost" size="sm" onClick={fetchSimilarHackathons} className="mt-2">
            Try Again
          </Button>
        </div>
      </Card>
    );
  }

  if (similarHackathons.length === 0) {
    return (
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-secondary-900 mb-4">Similar Hackathons</h3>
        <p className="text-sm text-secondary-500 text-center py-4">
          No similar hackathons found at the moment.
        </p>
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold text-secondary-900 mb-4 flex items-center">
        <svg className="h-5 w-5 mr-2 text-primary-600" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2L2 7v10c0 5.55 3.84 10 9 11 1.09-.87 2-1.92 2.71-3.08.4-.42.66-.96.85-1.54.14-.51.22-1.04.26-1.58.02-.37.03-.74.03-1.12V7l-10-5z"/>
        </svg>
        Similar Hackathons
      </h3>

      <p className="text-sm text-secondary-600 mb-4">
        AI found these hackathons similar to {currentTitle}:
      </p>

      <div className="space-y-4">
        {similarHackathons.map((hackathon) => (
          <div key={hackathon.id} className="border border-secondary-200 rounded-lg p-4 hover:bg-secondary-50 transition-colors">
            <Link href={`/hackathons/${hackathon.id}`}>
              <h4 className="font-medium text-secondary-900 hover:text-primary-600 transition-colors line-clamp-2 mb-2">
                {hackathon.title}
              </h4>
            </Link>

            {hackathon.short_description && (
              <p className="text-sm text-secondary-600 line-clamp-2 mb-3">
                {hackathon.short_description}
              </p>
            )}

            <div className="flex flex-wrap gap-2 mb-3">
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

            {hackathon.categories && hackathon.categories.length > 0 && (
              <div className="flex flex-wrap gap-1 mb-3">
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
                    +{hackathon.categories.length - 3}
                  </span>
                )}
              </div>
            )}

            <div className="flex justify-between items-center text-sm text-secondary-500">
              <span>{hackathon.location || 'Location TBD'}</span>
              {hackathon.source_platform && (
                <Badge variant="secondary" size="sm">
                  {hackathon.source_platform}
                </Badge>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 pt-4 border-t border-secondary-200">
        <Link href="/hackathons" className="text-sm text-primary-600 hover:text-primary-700 font-medium">
          Explore more hackathons →
        </Link>
      </div>
    </Card>
  );
};

export default SimilarHackathons;