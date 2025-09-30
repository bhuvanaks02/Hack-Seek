/**
 * Reusable Card component
 */
import React from 'react';
import { clsx } from 'clsx';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  padding?: 'none' | 'sm' | 'md' | 'lg';
  hover?: boolean;
  onClick?: () => void;
}

const Card: React.FC<CardProps> = ({
  children,
  className,
  padding = 'md',
  hover = false,
  onClick
}) => {
  const paddingClasses = {
    none: '',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8'
  };

  const cardClasses = clsx(
    'bg-white rounded-lg border border-secondary-200 shadow-sm',
    paddingClasses[padding],
    {
      'hover:shadow-md transition-shadow duration-200 cursor-pointer': hover || onClick,
    },
    className
  );

  if (onClick) {
    return (
      <div className={cardClasses} onClick={onClick} role="button" tabIndex={0}>
        {children}
      </div>
    );
  }

  return (
    <div className={cardClasses}>
      {children}
    </div>
  );
};

export default Card;