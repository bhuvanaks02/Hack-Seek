/**
 * Calendar view page for hackathons
 */
import React, { useState, useEffect } from 'react';
import { GetServerSideProps } from 'next';
import Layout from '@/components/layout/Layout';
import { Button, Card } from '@/components/ui';
import CalendarExport from '@/components/calendar/CalendarExport';
import { Hackathon, PaginatedResponse } from '@/types';

interface CalendarPageProps {
  initialHackathons?: PaginatedResponse<Hackathon>;
}

const CalendarPage: React.FC<CalendarPageProps> = ({ initialHackathons }) => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [viewMode, setViewMode] = useState<'month' | 'week' | 'list'>('month');
  const [hackathons, setHackathons] = useState<Hackathon[]>(initialHackathons?.data || []);

  const today = new Date();
  const currentMonth = currentDate.getMonth();
  const currentYear = currentDate.getFullYear();

  // Get first day of month and days in month
  const firstDayOfMonth = new Date(currentYear, currentMonth, 1);
  const lastDayOfMonth = new Date(currentYear, currentMonth + 1, 0);
  const daysInMonth = lastDayOfMonth.getDate();
  const startingDayOfWeek = firstDayOfMonth.getDay();

  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  const navigateMonth = (direction: 'prev' | 'next') => {
    const newDate = new Date(currentDate);
    newDate.setMonth(currentMonth + (direction === 'next' ? 1 : -1));
    setCurrentDate(newDate);
  };

  const getHackathonsForDate = (date: Date) => {
    return hackathons.filter(hackathon => {
      const startDate = hackathon.start_date ? new Date(hackathon.start_date) : null;
      const endDate = hackathon.end_date ? new Date(hackathon.end_date) : startDate;

      if (!startDate) return false;

      const targetDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());
      const hackathonStart = new Date(startDate.getFullYear(), startDate.getMonth(), startDate.getDate());
      const hackathonEnd = endDate ? new Date(endDate.getFullYear(), endDate.getMonth(), endDate.getDate()) : hackathonStart;

      return targetDate >= hackathonStart && targetDate <= hackathonEnd;
    });
  };

  const renderCalendarDays = () => {
    const days = [];
    const totalCells = Math.ceil((daysInMonth + startingDayOfWeek) / 7) * 7;

    for (let i = 0; i < totalCells; i++) {
      const dayNumber = i - startingDayOfWeek + 1;
      const isCurrentMonth = dayNumber > 0 && dayNumber <= daysInMonth;
      const date = new Date(currentYear, currentMonth, dayNumber);
      const isToday = isCurrentMonth &&
        date.getDate() === today.getDate() &&
        date.getMonth() === today.getMonth() &&
        date.getFullYear() === today.getFullYear();

      const dayHackathons = isCurrentMonth ? getHackathonsForDate(date) : [];

      days.push(
        <div
          key={i}
          className={`min-h-[100px] p-2 border border-secondary-200 ${
            isCurrentMonth ? 'bg-white' : 'bg-secondary-50'
          } ${isToday ? 'bg-primary-50 border-primary-300' : ''}`}
        >
          {isCurrentMonth && (
            <>
              <div className={`text-sm font-medium mb-1 ${isToday ? 'text-primary-700' : 'text-secondary-900'}`}>
                {dayNumber}
              </div>
              <div className="space-y-1">
                {dayHackathons.slice(0, 2).map((hackathon, index) => (
                  <div
                    key={hackathon.id}
                    className="text-xs p-1 bg-primary-100 text-primary-800 rounded truncate"
                    title={hackathon.title}
                  >
                    {hackathon.title}
                  </div>
                ))}
                {dayHackathons.length > 2 && (
                  <div className="text-xs text-secondary-500">
                    +{dayHackathons.length - 2} more
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      );
    }

    return days;
  };

  const renderListView = () => {
    const upcomingHackathons = hackathons
      .filter(h => h.start_date && new Date(h.start_date) >= today)
      .sort((a, b) => new Date(a.start_date!).getTime() - new Date(b.start_date!).getTime());

    return (
      <div className="space-y-4">
        {upcomingHackathons.map((hackathon) => (
          <Card key={hackathon.id} className="p-4">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-secondary-900 mb-2">
                  {hackathon.title}
                </h3>
                <div className="flex items-center text-sm text-secondary-600 mb-2">
                  <svg className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  {hackathon.start_date && new Date(hackathon.start_date).toLocaleDateString('en-US', {
                    weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}
                  {hackathon.end_date && ` - ${new Date(hackathon.end_date).toLocaleDateString('en-US', {
                    weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}`}
                </div>
                <div className="flex items-center text-sm text-secondary-600 mb-3">
                  <svg className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  </svg>
                  {hackathon.location || 'Online'}
                </div>
                {hackathon.short_description && (
                  <p className="text-sm text-secondary-600 mb-3">
                    {hackathon.short_description}
                  </p>
                )}
              </div>
              <div className="ml-4 flex flex-col space-y-2">
                <CalendarExport hackathon={hackathon} variant="dropdown" />
                <Button
                  size="sm"
                  onClick={() => window.open(hackathon.registration_url || hackathon.website_url, '_blank')}
                >
                  Register
                </Button>
              </div>
            </div>
          </Card>
        ))}

        {upcomingHackathons.length === 0 && (
          <div className="text-center py-12">
            <svg className="mx-auto h-12 w-12 text-secondary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-secondary-900">No upcoming hackathons</h3>
            <p className="mt-1 text-sm text-secondary-500">
              Check back later for new events or explore all hackathons.
            </p>
          </div>
        )}
      </div>
    );
  };

  return (
    <Layout
      title="Calendar - HackSeek"
      description="View upcoming hackathons in calendar format and add them to your personal calendar."
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h1 className="text-3xl font-bold text-secondary-900">Hackathon Calendar</h1>
              <p className="mt-2 text-secondary-600">
                View upcoming hackathons and add them to your calendar
              </p>
            </div>

            <div className="mt-4 sm:mt-0 flex items-center space-x-2">
              <div className="flex border border-secondary-300 rounded-lg">
                <button
                  onClick={() => setViewMode('month')}
                  className={`px-3 py-2 text-sm font-medium rounded-l-lg ${
                    viewMode === 'month'
                      ? 'bg-primary-600 text-white'
                      : 'text-secondary-700 hover:bg-secondary-50'
                  }`}
                >
                  Month
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`px-3 py-2 text-sm font-medium rounded-r-lg ${
                    viewMode === 'list'
                      ? 'bg-primary-600 text-white'
                      : 'text-secondary-700 hover:bg-secondary-50'
                  }`}
                >
                  List
                </button>
              </div>
            </div>
          </div>
        </div>

        {viewMode === 'month' ? (
          <Card className="p-0 overflow-hidden">
            {/* Calendar header */}
            <div className="bg-secondary-50 px-6 py-4 border-b border-secondary-200">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold text-secondary-900">
                  {monthNames[currentMonth]} {currentYear}
                </h2>
                <div className="flex items-center space-x-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => navigateMonth('prev')}
                  >
                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                    </svg>
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setCurrentDate(new Date())}
                  >
                    Today
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => navigateMonth('next')}
                  >
                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </Button>
                </div>
              </div>
            </div>

            {/* Days of week header */}
            <div className="grid grid-cols-7 border-b border-secondary-200">
              {weekDays.map((day) => (
                <div
                  key={day}
                  className="p-3 text-sm font-medium text-secondary-700 text-center bg-secondary-50"
                >
                  {day}
                </div>
              ))}
            </div>

            {/* Calendar grid */}
            <div className="grid grid-cols-7">
              {renderCalendarDays()}
            </div>
          </Card>
        ) : (
          renderListView()
        )}
      </div>
    </Layout>
  );
};

export const getServerSideProps: GetServerSideProps = async () => {
  try {
    // Fetch upcoming hackathons for calendar view
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/hackathons?upcoming=true&size=100`);

    if (!response.ok) {
      throw new Error('Failed to fetch hackathons');
    }

    const data: PaginatedResponse<Hackathon> = await response.json();

    return {
      props: {
        initialHackathons: data
      }
    };
  } catch (error) {
    console.error('Error fetching hackathons for calendar:', error);

    return {
      props: {
        initialHackathons: {
          data: [],
          total: 0,
          page: 1,
          pages: 1,
          size: 100
        }
      }
    };
  }
};

export default CalendarPage;