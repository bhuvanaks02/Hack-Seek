/**
 * Main layout wrapper component
 */
import React from 'react';
import Head from 'next/head';
import Header from './Header';
import Footer from './Footer';
import ErrorBoundary from '../ErrorBoundary';

interface LayoutProps {
  children: React.ReactNode;
  title?: string;
  description?: string;
  user?: any; // Will be typed properly with auth context
}

const Layout: React.FC<LayoutProps> = ({
  children,
  title = 'HackSeek - Discover Hackathons Worldwide',
  description = 'Find and discover hackathons worldwide with AI-powered search and personalized recommendations.',
  user
}) => {
  return (
    <>
      <Head>
        <title>{title}</title>
        <meta name="description" content={description} />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />

        {/* Open Graph */}
        <meta property="og:title" content={title} />
        <meta property="og:description" content={description} />
        <meta property="og:type" content="website" />
        <meta property="og:site_name" content="HackSeek" />

        {/* Twitter */}
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content={title} />
        <meta name="twitter:description" content={description} />
      </Head>

      <div className="min-h-screen flex flex-col bg-secondary-50">
        <ErrorBoundary>
          <Header user={user} />

          <main className="flex-grow">
            {children}
          </main>

          <Footer />
        </ErrorBoundary>
      </div>
    </>
  );
};

export default Layout;