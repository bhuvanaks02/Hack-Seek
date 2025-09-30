/**
 * Individual hackathon detail page
 */
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { GetServerSideProps } from 'next';
import { format } from 'date-fns';
import Layout from '@/components/layout/Layout';
import { Button, Badge, Card } from '@/components/ui';
import { Hackathon } from '@/types';

interface HackathonDetailPageProps {
  hackathon?: Hackathon;
  error?: string;
}

const HackathonDetailPage: React.FC<HackathonDetailPageProps> = ({ hackathon, error }) => {
  const router = useRouter();
  const [isFavorited, setIsFavorited] = useState(false);

  if (error || !hackathon) {
    return (
      <Layout title="Hackathon Not Found">
        <div className="max-w-4xl mx-auto px-4 py-16 text-center">
          <h1 className="text-3xl font-bold text-secondary-900 mb-4">
            {error || 'Hackathon not found'}
          </h1>
          <Button onClick={() => router.push('/hackathons')}>
            Back to Hackathons
          </Button>
        </div>
      </Layout>
    );
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'TBD';
    try {
      return format(new Date(dateString), 'MMMM dd, yyyy');
    } catch {
      return 'Invalid date';
    }
  };

  const getDaysRemaining = () => {
    if (!hackathon.registration_deadline) return null;
    const deadline = new Date(hackathon.registration_deadline);
    const now = new Date();
    const diffTime = deadline.getTime() - now.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays > 0 ? diffDays : 0;
  };

  const daysRemaining = getDaysRemaining();

  return (
    <Layout
      title={`${hackathon.title} - HackSeek`}
      description={hackathon.short_description || hackathon.description}
    >
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex justify-between items-start mb-4">
            <div className="flex-1">
              <h1 className="text-3xl md:text-4xl font-bold text-secondary-900 mb-2">
                {hackathon.title}
              </h1>
              {hackathon.organizer && (
                <p className="text-lg text-secondary-600">
                  Organized by {hackathon.organizer}
                </p>
              )}
            </div>

            <button
              onClick={() => setIsFavorited(!isFavorited)}
              className={`p-3 rounded-full hover:bg-secondary-100 transition-colors ${
                isFavorited ? 'text-red-500' : 'text-secondary-400'
              }`}
            >
              <svg className="h-6 w-6" fill={isFavorited ? 'currentColor' : 'none'} viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </button>
          </div>

          {/* Status badges */}
          <div className="flex flex-wrap gap-3 mb-6">
            {hackathon.is_online && (
              <Badge variant="primary">Online Event</Badge>
            )}
            {hackathon.difficulty_level && (
              <Badge variant="secondary">{hackathon.difficulty_level}</Badge>
            )}
            {hackathon.prize_money && hackathon.prize_money > 0 && (
              <Badge variant="success">
                ${hackathon.prize_money.toLocaleString()} Prize
              </Badge>
            )}
            {daysRemaining !== null && daysRemaining <= 7 && (
              <Badge variant={daysRemaining === 0 ? 'error' : 'warning'}>
                {daysRemaining === 0 ? 'Deadline Today' : `${daysRemaining} days left`}
              </Badge>
            )}
            {hackathon.source_platform && (
              <Badge variant="secondary">{hackathon.source_platform}</Badge>
            )}
          </div>

          {/* Action buttons */}
          <div className="flex flex-col sm:flex-row gap-4">
            <Button
              size="lg"
              onClick={() => window.open(hackathon.registration_url || hackathon.website_url, '_blank')}
              className="bg-primary-600 hover:bg-primary-700"
            >
              Register Now
              <svg className="ml-2 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </Button>
            {hackathon.website_url && hackathon.website_url !== hackathon.registration_url && (
              <Button
                variant="ghost"
                size="lg"
                onClick={() => window.open(hackathon.website_url, '_blank')}
              >
                Visit Website
              </Button>
            )}
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {/* Main content */}
          <div className="md:col-span-2 space-y-8">
            {/* Description */}
            <Card>
              <h2 className="text-xl font-semibold text-secondary-900 mb-4">About</h2>
              <div className="prose prose-secondary max-w-none">
                {hackathon.description ? (
                  <p className="text-secondary-700 whitespace-pre-wrap">
                    {hackathon.description}
                  </p>
                ) : hackathon.short_description ? (
                  <p className="text-secondary-700">
                    {hackathon.short_description}
                  </p>
                ) : (
                  <p className="text-secondary-500 italic">
                    No description available.
                  </p>
                )}
              </div>
            </Card>

            {/* Categories */}
            {hackathon.categories && hackathon.categories.length > 0 && (
              <Card>
                <h2 className="text-xl font-semibold text-secondary-900 mb-4">Categories</h2>
                <div className="flex flex-wrap gap-2">
                  {hackathon.categories.map((category, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-secondary-100 text-secondary-700 rounded-full text-sm"
                    >
                      {category}
                    </span>
                  ))}
                </div>
              </Card>
            )}

            {/* Technologies */}
            {hackathon.technologies && hackathon.technologies.length > 0 && (
              <Card>
                <h2 className="text-xl font-semibold text-secondary-900 mb-4">Technologies</h2>
                <div className="flex flex-wrap gap-2">
                  {hackathon.technologies.map((tech, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-primary-50 text-primary-700 rounded-full text-sm border border-primary-200"
                    >
                      {tech}
                    </span>
                  ))}
                </div>
              </Card>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Event details */}
            <Card>
              <h3 className="text-lg font-semibold text-secondary-900 mb-4">Event Details</h3>
              <div className="space-y-4 text-sm">
                <div className="flex justify-between">
                  <span className="text-secondary-600">Start Date:</span>
                  <span className="font-medium">{formatDate(hackathon.start_date)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-secondary-600">End Date:</span>
                  <span className="font-medium">{formatDate(hackathon.end_date)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-secondary-600">Registration Deadline:</span>
                  <span className="font-medium">
                    {formatDate(hackathon.registration_deadline)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-secondary-600">Location:</span>
                  <span className="font-medium">
                    {hackathon.location || (hackathon.is_online ? 'Online' : 'TBD')}
                  </span>
                </div>
                {hackathon.prize_money && hackathon.prize_money > 0 && (
                  <div className="flex justify-between">
                    <span className="text-secondary-600">Prize Money:</span>
                    <span className="font-semibold text-green-600">
                      ${hackathon.prize_money.toLocaleString()}
                    </span>
                  </div>
                )}
                {hackathon.max_team_size && (
                  <div className="flex justify-between">
                    <span className="text-secondary-600">Max Team Size:</span>
                    <span className="font-medium">{hackathon.max_team_size}</span>
                  </div>
                )}
              </div>
            </Card>

            {/* Quick actions */}
            <Card>
              <h3 className="text-lg font-semibold text-secondary-900 mb-4">Quick Actions</h3>
              <div className="space-y-3">
                <Button
                  variant="ghost"
                  size="sm"
                  className="w-full justify-start"
                  onClick={() => {
                    const text = `Check out this hackathon: ${hackathon.title} - ${window.location.href}`;
                    navigator.clipboard.writeText(text);
                  }}
                >
                  <svg className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                  Copy Link
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  className="w-full justify-start"
                  onClick={() => {
                    const subject = encodeURIComponent(`Check out: ${hackathon.title}`);
                    const body = encodeURIComponent(`I found this interesting hackathon: ${hackathon.title}\n\n${hackathon.short_description || ''}\n\nCheck it out: ${window.location.href}`);
                    window.open(`mailto:?subject=${subject}&body=${body}`);
                  }}
                >
                  <svg className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  Share via Email
                </Button>
                {hackathon.start_date && (
                  <Button
                    variant="ghost"
                    size="sm"
                    className="w-full justify-start"
                    onClick={() => {
                      const startDate = new Date(hackathon.start_date!);
                      const endDate = hackathon.end_date ? new Date(hackathon.end_date) : new Date(startDate.getTime() + 24 * 60 * 60 * 1000);

                      const formatCalendarDate = (date: Date) => {
                        return date.toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z';
                      };

                      const calendarUrl = `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${encodeURIComponent(hackathon.title)}&dates=${formatCalendarDate(startDate)}/${formatCalendarDate(endDate)}&details=${encodeURIComponent(hackathon.short_description || '')}&location=${encodeURIComponent(hackathon.location || 'Online')}`;
                      window.open(calendarUrl, '_blank');
                    }}
                  >
                    <svg className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    Add to Calendar
                  </Button>
                )}
              </div>
            </Card>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export const getServerSideProps: GetServerSideProps = async (context) => {
  const { id } = context.params!;

  try {
    // This would normally fetch from your API
    // For now, return mock data or handle the API call
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/hackathons/${id}`);

    if (!response.ok) {
      return {
        props: {
          error: 'Hackathon not found'
        }
      };
    }

    const hackathon = await response.json();

    return {
      props: {
        hackathon
      }
    };
  } catch (error) {
    return {
      props: {
        error: 'Failed to load hackathon details'
      }
    };
  }
};

export default HackathonDetailPage;