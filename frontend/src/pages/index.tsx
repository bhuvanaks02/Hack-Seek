/**
 * Home page
 */
import React from 'react';
import Link from 'next/link';
import Layout from '@/components/layout/Layout';
import { Button, Card } from '@/components/ui';

const HomePage: React.FC = () => {
  const features = [
    {
      icon: (
        <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      ),
      title: 'Smart Search',
      description: 'Find hackathons using AI-powered search with natural language queries.'
    },
    {
      icon: (
        <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      title: 'Global Coverage',
      description: 'Discover hackathons from Devpost, MLH, Unstop, and other major platforms.'
    },
    {
      icon: (
        <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      ),
      title: 'Calendar Integration',
      description: 'Export hackathons to your calendar and never miss registration deadlines.'
    },
    {
      icon: (
        <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      ),
      title: 'Real-time Updates',
      description: 'Get notified about new hackathons and deadline reminders.'
    }
  ];

  const stats = [
    { label: 'Active Hackathons', value: '500+' },
    { label: 'Total Prize Money', value: '$2M+' },
    { label: 'Countries Covered', value: '50+' },
    { label: 'Happy Developers', value: '10K+' }
  ];

  return (
    <Layout
      title="HackSeek - Discover Hackathons Worldwide"
      description="Find and discover hackathons worldwide with AI-powered search and personalized recommendations."
    >
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-primary-600 to-primary-800 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
          <div className="text-center">
            <h1 className="text-3xl sm:text-4xl md:text-6xl font-bold mb-6">
              Discover Your Next
              <span className="block text-primary-200">Hackathon Adventure</span>
            </h1>
            <p className="text-lg sm:text-xl md:text-2xl text-primary-100 mb-8 max-w-3xl mx-auto">
              Find hackathons worldwide with AI-powered search. Filter by location, tech stack,
              prize money, and get personalized recommendations.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/hackathons">
                <Button size="lg" className="w-full sm:w-auto bg-white text-primary-600 hover:bg-primary-50">
                  Explore Hackathons
                </Button>
              </Link>
              <Link href="/auth/register">
                <Button variant="ghost" size="lg" className="w-full sm:w-auto border-2 border-white text-white hover:bg-white hover:text-primary-600">
                  Sign Up Free
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="bg-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-3xl md:text-4xl font-bold text-primary-600 mb-2">
                  {stat.value}
                </div>
                <div className="text-secondary-600">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="bg-secondary-50 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-secondary-900 mb-4">
              Everything You Need to Find Hackathons
            </h2>
            <p className="text-xl text-secondary-600 max-w-3xl mx-auto">
              Our platform aggregates hackathons from around the world and uses AI to help you
              find the perfect match for your skills and interests.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8">
            {features.map((feature, index) => (
              <Card key={index} className="text-center h-full">
                <div className="text-primary-600 mb-4 flex justify-center">
                  {feature.icon}
                </div>
                <h3 className="text-lg lg:text-xl font-semibold text-secondary-900 mb-3">
                  {feature.title}
                </h3>
                <p className="text-sm lg:text-base text-secondary-600">
                  {feature.description}
                </p>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-secondary-900 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Ready to Find Your Next Hackathon?
          </h2>
          <p className="text-xl text-secondary-300 mb-8 max-w-2xl mx-auto">
            Join thousands of developers who use HackSeek to discover amazing hackathons
            and build incredible projects.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/hackathons">
              <Button size="lg" className="w-full sm:w-auto bg-primary-600 hover:bg-primary-700">
                Start Exploring
              </Button>
            </Link>
            <Link href="/featured">
              <Button variant="ghost" size="lg" className="w-full sm:w-auto border-2 border-white text-white hover:bg-white hover:text-secondary-900">
                View Featured
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </Layout>
  );
};

export default HomePage;