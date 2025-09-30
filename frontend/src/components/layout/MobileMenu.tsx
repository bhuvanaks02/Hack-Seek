/**
 * Mobile navigation menu
 */
import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Button } from '../ui';

interface MobileMenuProps {
  isOpen: boolean;
  onClose: () => void;
  user?: any;
}

const MobileMenu: React.FC<MobileMenuProps> = ({ isOpen, onClose, user }) => {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  const navigationLinks = [
    { name: 'Home', href: '/' },
    { name: 'Find Hackathons', href: '/hackathons' },
    { name: 'Featured', href: '/featured' },
    { name: 'Calendar', href: '/calendar' },
    { name: 'About', href: '/about' },
  ];

  return (
    <div className="fixed inset-0 z-50 lg:hidden">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50"
        onClick={onClose}
      />

      {/* Menu panel */}
      <div className="fixed inset-y-0 right-0 w-full max-w-sm bg-white shadow-xl">
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-secondary-200">
            <Link href="/" className="text-xl font-bold text-primary-600">
              HackSeek
            </Link>
            <button
              onClick={onClose}
              className="p-2 rounded-lg hover:bg-secondary-100 transition-colors"
            >
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-1">
            {navigationLinks.map((link) => (
              <Link
                key={link.name}
                href={link.href}
                className="block px-3 py-3 text-base font-medium text-secondary-700 hover:text-primary-600 hover:bg-secondary-50 rounded-lg transition-colors"
                onClick={onClose}
              >
                {link.name}
              </Link>
            ))}
          </nav>

          {/* User section */}
          <div className="border-t border-secondary-200 p-4 space-y-3">
            {user ? (
              <>
                <div className="flex items-center space-x-3 px-3 py-2">
                  <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center">
                    <span className="text-sm font-medium text-white">
                      {user.first_name?.[0] || user.email[0].toUpperCase()}
                    </span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-secondary-900 truncate">
                      {user.first_name ? `${user.first_name} ${user.last_name || ''}`.trim() : user.email}
                    </p>
                    <p className="text-sm text-secondary-500 truncate">{user.email}</p>
                  </div>
                </div>
                <div className="space-y-1">
                  <Link
                    href="/profile"
                    className="block px-3 py-2 text-sm text-secondary-700 hover:text-primary-600 hover:bg-secondary-50 rounded-lg transition-colors"
                    onClick={onClose}
                  >
                    Profile
                  </Link>
                  <Link
                    href="/favorites"
                    className="block px-3 py-2 text-sm text-secondary-700 hover:text-primary-600 hover:bg-secondary-50 rounded-lg transition-colors"
                    onClick={onClose}
                  >
                    My Favorites
                  </Link>
                  <button
                    className="w-full text-left px-3 py-2 text-sm text-secondary-700 hover:text-primary-600 hover:bg-secondary-50 rounded-lg transition-colors"
                    onClick={() => {
                      // Handle logout
                      onClose();
                    }}
                  >
                    Sign Out
                  </button>
                </div>
              </>
            ) : (
              <div className="space-y-3">
                <Link href="/auth/login" onClick={onClose}>
                  <Button variant="ghost" className="w-full justify-center">
                    Sign In
                  </Button>
                </Link>
                <Link href="/auth/register" onClick={onClose}>
                  <Button className="w-full justify-center">
                    Get Started
                  </Button>
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MobileMenu;