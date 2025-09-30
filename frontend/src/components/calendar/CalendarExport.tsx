/**
 * Calendar export component for hackathons
 */
import React, { useState } from 'react';
import { Button } from '../ui';
import { Hackathon } from '@/types';

interface CalendarExportProps {
  hackathon: Hackathon;
  variant?: 'button' | 'dropdown';
  className?: string;
}

const CalendarExport: React.FC<CalendarExportProps> = ({
  hackathon,
  variant = 'button',
  className = ''
}) => {
  const [isOpen, setIsOpen] = useState(false);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z';
  };

  const generateCalendarUrl = (provider: 'google' | 'outlook' | 'yahoo' | 'ics') => {
    if (!hackathon.start_date) return '#';

    const startDate = formatDate(hackathon.start_date);
    const endDate = hackathon.end_date
      ? formatDate(hackathon.end_date)
      : formatDate(new Date(new Date(hackathon.start_date).getTime() + 24 * 60 * 60 * 1000).toISOString());

    const title = encodeURIComponent(hackathon.title);
    const description = encodeURIComponent(
      hackathon.description || hackathon.short_description || 'Hackathon event'
    );
    const location = encodeURIComponent(hackathon.location || 'Online');

    switch (provider) {
      case 'google':
        return `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${title}&dates=${startDate}/${endDate}&details=${description}&location=${location}`;

      case 'outlook':
        return `https://outlook.live.com/calendar/0/deeplink/compose?subject=${title}&startdt=${startDate}&enddt=${endDate}&body=${description}&location=${location}`;

      case 'yahoo':
        return `https://calendar.yahoo.com/?v=60&view=d&type=20&title=${title}&st=${startDate}&et=${endDate}&desc=${description}&in_loc=${location}`;

      case 'ics':
        return generateICSFile();

      default:
        return '#';
    }
  };

  const generateICSFile = () => {
    if (!hackathon.start_date) return '#';

    const startDate = formatDate(hackathon.start_date);
    const endDate = hackathon.end_date
      ? formatDate(hackathon.end_date)
      : formatDate(new Date(new Date(hackathon.start_date).getTime() + 24 * 60 * 60 * 1000).toISOString());

    const icsContent = [
      'BEGIN:VCALENDAR',
      'VERSION:2.0',
      'PRODID:-//HackSeek//Calendar Export//EN',
      'BEGIN:VEVENT',
      `UID:hackathon-${hackathon.id}@hackseek.com`,
      `DTSTART:${startDate}`,
      `DTEND:${endDate}`,
      `SUMMARY:${hackathon.title}`,
      `DESCRIPTION:${hackathon.description || hackathon.short_description || ''}`,
      `LOCATION:${hackathon.location || 'Online'}`,
      `URL:${hackathon.website_url || ''}`,
      'END:VEVENT',
      'END:VCALENDAR'
    ].join('\r\n');

    const blob = new Blob([icsContent], { type: 'text/calendar;charset=utf-8' });
    return URL.createObjectURL(blob);
  };

  const handleDownload = (provider: string) => {
    if (provider === 'ics') {
      const url = generateICSFile();
      const link = document.createElement('a');
      link.href = url;
      link.download = `${hackathon.title.replace(/[^a-z0-9]/gi, '_')}.ics`;
      link.click();
      URL.revokeObjectURL(url);
    } else {
      window.open(generateCalendarUrl(provider as any), '_blank');
    }
    setIsOpen(false);
  };

  if (variant === 'button') {
    return (
      <Button
        variant="ghost"
        size="sm"
        onClick={() => handleDownload('google')}
        className={className}
      >
        <svg className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        Add to Calendar
      </Button>
    );
  }

  return (
    <div className={`relative ${className}`}>
      <Button
        variant="ghost"
        size="sm"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full justify-start"
      >
        <svg className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        Add to Calendar
        <svg className="h-4 w-4 ml-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </Button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute top-full left-0 mt-1 w-48 bg-white rounded-lg shadow-lg border border-secondary-200 z-20">
            <div className="py-1">
              <button
                onClick={() => handleDownload('google')}
                className="flex items-center w-full px-4 py-2 text-sm text-secondary-700 hover:bg-secondary-50"
              >
                <svg className="h-4 w-4 mr-3" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                  <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                  <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                  <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
                </svg>
                Google Calendar
              </button>

              <button
                onClick={() => handleDownload('outlook')}
                className="flex items-center w-full px-4 py-2 text-sm text-secondary-700 hover:bg-secondary-50"
              >
                <svg className="h-4 w-4 mr-3" viewBox="0 0 24 24" fill="#0078d4">
                  <path d="M7 18h4V6H7v12zm11-7.5V18h-2v-7.5h2zm-2-1.5V7h2v2h-2z"/>
                </svg>
                Outlook
              </button>

              <button
                onClick={() => handleDownload('yahoo')}
                className="flex items-center w-full px-4 py-2 text-sm text-secondary-700 hover:bg-secondary-50"
              >
                <svg className="h-4 w-4 mr-3" viewBox="0 0 24 24" fill="#6001d2">
                  <path d="M12 0C5.383 0 0 5.383 0 12s5.383 12 12 12 12-5.383 12-12S18.617 0 12 0zm4.879 17.07l-3.542-6.103-3.542 6.103H7.6l5.4-8.957L7.6 6.93h2.195l3.205 5.545L16.205 6.93H18.4l-5.4 8.183 5.4 8.957h-1.521z"/>
                </svg>
                Yahoo Calendar
              </button>

              <div className="border-t border-secondary-200 my-1" />

              <button
                onClick={() => handleDownload('ics')}
                className="flex items-center w-full px-4 py-2 text-sm text-secondary-700 hover:bg-secondary-50"
              >
                <svg className="h-4 w-4 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Download .ics file
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default CalendarExport;