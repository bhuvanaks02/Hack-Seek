/**
 * AI-powered recommendations page
 */
import React, { useState, useEffect } from 'react';
import { GetServerSideProps } from 'next';
import Layout from '@/components/layout/Layout';
import RecommendationCard from '@/components/ai/RecommendationCard';
import { Button, Card } from '@/components/ui';

interface RecommendationData {
  hackathon: any;
  recommendation_score: number;
  reasons: string[];
}

interface RecommendationsPageProps {
  initialRecommendations?: RecommendationData[];
  userId?: string;
}

const RecommendationsPage: React.FC<RecommendationsPageProps> = ({
  initialRecommendations = [],
  userId
}) => {
  const [recommendations, setRecommendations] = useState<RecommendationData[]>(initialRecommendations);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [favorites, setFavorites] = useState<string[]>([]);

  const fetchRecommendations = async () => {
    if (!userId) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/hackathons/ai/recommendations?user_id=${userId}&limit=10`);

      if (!response.ok) {
        throw new Error('Failed to fetch recommendations');
      }

      const data = await response.json();
      setRecommendations(data);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    fetchRecommendations();
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

  const getPersonalizationTips = () => {
    return [
      "Complete your profile with skills and interests for better recommendations",
      "Mark hackathons as favorites to improve future suggestions",
      "Participate in hackathons to build your activity history",
      "Update your experience level to get appropriate difficulty matches"
    ];
  };

  return (
    <Layout
      title="AI Recommendations - HackSeek"
      description="Get personalized hackathon recommendations powered by AI based on your interests and skills."
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h1 className="text-3xl font-bold text-secondary-900 flex items-center">
                <svg className="h-8 w-8 mr-3 text-primary-600" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2L2 7v10c0 5.55 3.84 10 9 11 1.09-.87 2-1.92 2.71-3.08.4-.42.66-.96.85-1.54.14-.51.22-1.04.26-1.58.02-.37.03-.74.03-1.12V7l-10-5z"/>
                </svg>
                AI Recommendations
              </h1>
              <p className="mt-2 text-secondary-600">
                Personalized hackathon suggestions based on your profile and interests
              </p>
            </div>

            <div className="mt-4 sm:mt-0">
              <Button
                onClick={handleRefresh}
                disabled={loading}
                loading={loading}
                variant="ghost"
              >
                <svg className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Refresh Recommendations
              </Button>
            </div>
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

        <div className="grid lg:grid-cols-4 gap-8">
          {/* Main content */}
          <div className="lg:col-span-3">
            {recommendations.length > 0 ? (
              <div className="space-y-6">
                <div className="grid gap-6">
                  {recommendations.map((recommendation, index) => (
                    <RecommendationCard
                      key={recommendation.hackathon.id}
                      recommendation={recommendation}
                      onFavorite={handleFavorite}
                      isFavorited={favorites.includes(recommendation.hackathon.id)}
                    />
                  ))}
                </div>

                {/* Load more button */}
                <div className="text-center">
                  <Button
                    onClick={handleRefresh}
                    variant="ghost"
                    disabled={loading}
                  >
                    Load More Recommendations
                  </Button>
                </div>
              </div>
            ) : !loading && !userId ? (
              <Card className="text-center py-12">
                <svg className="mx-auto h-12 w-12 text-secondary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                <h3 className="mt-2 text-sm font-medium text-secondary-900">Sign in required</h3>
                <p className="mt-1 text-sm text-secondary-500">
                  Sign in to get personalized hackathon recommendations powered by AI.
                </p>
                <div className="mt-6">
                  <Button onClick={() => window.location.href = '/auth/login'}>
                    Sign In
                  </Button>
                </div>
              </Card>
            ) : !loading ? (
              <Card className="text-center py-12">
                <svg className="mx-auto h-12 w-12 text-secondary-400" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2L2 7v10c0 5.55 3.84 10 9 11 1.09-.87 2-1.92 2.71-3.08.4-.42.66-.96.85-1.54.14-.51.22-1.04.26-1.58.02-.37.03-.74.03-1.12V7l-10-5z"/>
                </svg>
                <h3 className="mt-2 text-sm font-medium text-secondary-900">No recommendations yet</h3>
                <p className="mt-1 text-sm text-secondary-500">
                  Complete your profile to get AI-powered hackathon recommendations.
                </p>
                <div className="mt-6">
                  <Button onClick={() => window.location.href = '/profile'}>
                    Complete Profile
                  </Button>
                </div>
              </Card>
            ) : (
              <div className="space-y-6">
                {/* Loading skeleton */}
                {[...Array(3)].map((_, index) => (
                  <Card key={index} className="p-6">
                    <div className="animate-pulse">
                      <div className="flex justify-between items-start mb-4">
                        <div className="h-4 bg-secondary-200 rounded w-32"></div>
                        <div className="h-8 w-8 bg-secondary-200 rounded-full"></div>
                      </div>
                      <div className="h-6 bg-secondary-200 rounded w-3/4 mb-2"></div>
                      <div className="h-4 bg-secondary-200 rounded w-1/2 mb-4"></div>
                      <div className="space-y-2 mb-4">
                        <div className="h-3 bg-secondary-200 rounded w-full"></div>
                        <div className="h-3 bg-secondary-200 rounded w-3/4"></div>
                      </div>
                      <div className="flex space-x-2">
                        <div className="h-6 bg-secondary-200 rounded w-16"></div>
                        <div className="h-6 bg-secondary-200 rounded w-20"></div>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            {/* How it works */}
            <Card className="p-6">
              <h3 className="text-lg font-medium text-secondary-900 mb-4 flex items-center">
                <svg className="h-5 w-5 mr-2 text-primary-600" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2L2 7v10c0 5.55 3.84 10 9 11 1.09-.87 2-1.92 2.71-3.08.4-.42.66-.96.85-1.54.14-.51.22-1.04.26-1.58.02-.37.03-.74.03-1.12V7l-10-5z"/>
                </svg>
                How AI Recommendations Work
              </h3>
              <div className="space-y-3 text-sm text-secondary-600">
                <div className="flex items-start">
                  <span className="flex-shrink-0 w-6 h-6 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center text-xs font-medium mr-3 mt-0.5">
                    1
                  </span>
                  <p>We analyze your skills, interests, and experience level</p>
                </div>
                <div className="flex items-start">
                  <span className="flex-shrink-0 w-6 h-6 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center text-xs font-medium mr-3 mt-0.5">
                    2
                  </span>
                  <p>AI matches you with relevant hackathons based on content similarity</p>
                </div>
                <div className="flex items-start">
                  <span className="flex-shrink-0 w-6 h-6 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center text-xs font-medium mr-3 mt-0.5">
                    3
                  </span>
                  <p>Recommendations improve as you interact with the platform</p>
                </div>
              </div>
            </Card>

            {/* Personalization tips */}
            <Card className="p-6">
              <h3 className="text-lg font-medium text-secondary-900 mb-4">
                Improve Your Recommendations
              </h3>
              <div className="space-y-3">
                {getPersonalizationTips().map((tip, index) => (
                  <div key={index} className="flex items-start">
                    <svg className="h-4 w-4 text-primary-600 mr-2 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                    </svg>
                    <p className="text-sm text-secondary-600">{tip}</p>
                  </div>
                ))}
              </div>
            </Card>

            {/* Quick actions */}
            <Card className="p-6">
              <h3 className="text-lg font-medium text-secondary-900 mb-4">Quick Actions</h3>
              <div className="space-y-3">
                <Button
                  variant="ghost"
                  size="sm"
                  className="w-full justify-start"
                  onClick={() => window.location.href = '/profile'}
                >
                  <svg className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                  Edit Profile
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  className="w-full justify-start"
                  onClick={() => window.location.href = '/favorites'}
                >
                  <svg className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                  </svg>
                  View Favorites
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  className="w-full justify-start"
                  onClick={() => window.location.href = '/hackathons'}
                >
                  <svg className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                  Browse All
                </Button>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export const getServerSideProps: GetServerSideProps = async (context) => {
  // In a real app, you'd get the user ID from session/cookies
  const userId = context.query.user_id as string || null;

  if (!userId) {
    return {
      props: {
        initialRecommendations: [],
        userId: null
      }
    };
  }

  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/hackathons/ai/recommendations?user_id=${userId}&limit=10`);

    if (!response.ok) {
      throw new Error('Failed to fetch recommendations');
    }

    const recommendations = await response.json();

    return {
      props: {
        initialRecommendations: recommendations,
        userId
      }
    };
  } catch (error) {
    console.error('Error fetching recommendations:', error);

    return {
      props: {
        initialRecommendations: [],
        userId
      }
    };
  }
};

export default RecommendationsPage;