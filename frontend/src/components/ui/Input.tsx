/**
 * Reusable Input component
 */
import React from 'react';
import { clsx } from 'clsx';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  helpText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

const Input: React.FC<InputProps> = ({
  label,
  error,
  helperText,
  helpText,
  leftIcon,
  rightIcon,
  className,
  id,
  ...props
}) => {
  const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;

  const inputClasses = clsx(
    'block w-full rounded-lg border px-3 py-2 text-sm',
    'focus:outline-none focus:ring-2 focus:ring-offset-0',
    'disabled:opacity-50 disabled:cursor-not-allowed',
    {
      'border-error-300 focus:border-error-500 focus:ring-error-500': error,
      'border-secondary-300 focus:border-primary-500 focus:ring-primary-500': !error,
      'pl-10': leftIcon,
      'pr-10': rightIcon,
    },
    className
  );

  return (
    <div>
      {label && (
        <label htmlFor={inputId} className="block text-sm font-medium text-secondary-700 mb-1">
          {label}
        </label>
      )}

      <div className="relative">
        {leftIcon && (
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <div className="h-5 w-5 text-secondary-400">
              {leftIcon}
            </div>
          </div>
        )}

        <input
          id={inputId}
          className={inputClasses}
          {...props}
        />

        {rightIcon && (
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
            <div className="h-5 w-5 text-secondary-400">
              {rightIcon}
            </div>
          </div>
        )}
      </div>

      {error && (
        <p className="mt-1 text-sm text-error-600">{error}</p>
      )}

      {(helperText || helpText) && !error && (
        <p className="mt-1 text-sm text-secondary-500">{helperText || helpText}</p>
      )}
    </div>
  );
};

export default Input;