/**
 * React Error Boundary component for catching and handling React errors.
 */
import React from 'react';
import { handleComponentError, logError } from '../utils/errorHandler';

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
  errorInfo?: React.ErrorInfo;
}

interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ComponentType<ErrorFallbackProps>;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
  showDetails?: boolean;
}

interface ErrorFallbackProps {
  error: Error;
  resetError: () => void;
  showDetails?: boolean;
}

/**
 * Default error fallback component
 */
const DefaultErrorFallback: React.FC<ErrorFallbackProps> = ({
  error,
  resetError,
  showDetails = false
}) => {
  const isDevelopment = process.env.NODE_ENV === 'development';

  return (
    <div className="error-boundary">
      <div className="error-boundary-content">
        <h2>Something went wrong</h2>
        <p>We're sorry, but something unexpected happened. Please try refreshing the page.</p>

        <div className="error-boundary-actions">
          <button
            onClick={resetError}
            className="btn btn-primary"
          >
            Try Again
          </button>

          <button
            onClick={() => window.location.reload()}
            className="btn btn-secondary"
          >
            Refresh Page
          </button>
        </div>

        {(isDevelopment || showDetails) && (
          <details className="error-boundary-details">
            <summary>Error Details (Development Only)</summary>
            <div className="error-boundary-error">
              <h4>Error Message:</h4>
              <pre>{error.message}</pre>

              {error.stack && (
                <>
                  <h4>Stack Trace:</h4>
                  <pre>{error.stack}</pre>
                </>
              )}
            </div>
          </details>
        )}
      </div>

      <style jsx>{`
        .error-boundary {
          min-height: 400px;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 2rem;
          background-color: #f8f9fa;
          border: 1px solid #dee2e6;
          border-radius: 8px;
          margin: 1rem 0;
        }

        .error-boundary-content {
          text-align: center;
          max-width: 600px;
        }

        .error-boundary h2 {
          color: #dc3545;
          margin-bottom: 1rem;
        }

        .error-boundary p {
          color: #6c757d;
          margin-bottom: 2rem;
          line-height: 1.5;
        }

        .error-boundary-actions {
          display: flex;
          gap: 1rem;
          justify-content: center;
          margin-bottom: 2rem;
        }

        .btn {
          padding: 0.75rem 1.5rem;
          border: none;
          border-radius: 4px;
          font-size: 1rem;
          cursor: pointer;
          transition: background-color 0.2s;
        }

        .btn-primary {
          background-color: #007bff;
          color: white;
        }

        .btn-primary:hover {
          background-color: #0056b3;
        }

        .btn-secondary {
          background-color: #6c757d;
          color: white;
        }

        .btn-secondary:hover {
          background-color: #545b62;
        }

        .error-boundary-details {
          text-align: left;
          margin-top: 2rem;
          padding: 1rem;
          background-color: #f1f3f4;
          border-radius: 4px;
        }

        .error-boundary-details summary {
          cursor: pointer;
          font-weight: bold;
          margin-bottom: 1rem;
        }

        .error-boundary-error h4 {
          margin: 1rem 0 0.5rem 0;
          color: #495057;
        }

        .error-boundary-error pre {
          background-color: #ffffff;
          padding: 1rem;
          border-radius: 4px;
          overflow-x: auto;
          white-space: pre-wrap;
          font-size: 0.875rem;
          line-height: 1.4;
          border: 1px solid #dee2e6;
        }
      `}</style>
    </div>
  );
};

/**
 * Error Boundary component
 */
export class ErrorBoundary extends React.Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log the error
    handleComponentError(error, errorInfo, 'ErrorBoundary');

    // Call custom error handler if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // Update state with error info
    this.setState({
      error,
      errorInfo,
    });
  }

  resetError = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined });
  };

  render() {
    if (this.state.hasError) {
      const FallbackComponent = this.props.fallback || DefaultErrorFallback;

      return (
        <FallbackComponent
          error={this.state.error!}
          resetError={this.resetError}
          showDetails={this.props.showDetails}
        />
      );
    }

    return this.props.children;
  }
}

/**
 * Hook for handling async errors in functional components
 */
export const useErrorHandler = () => {
  const [error, setError] = React.useState<Error | null>(null);

  const resetError = React.useCallback(() => {
    setError(null);
  }, []);

  const handleError = React.useCallback((error: Error) => {
    logError(error, {
      component: 'useErrorHandler',
      action: 'async_error',
    });
    setError(error);
  }, []);

  React.useEffect(() => {
    if (error) {
      throw error;
    }
  }, [error]);

  return { handleError, resetError };
};

/**
 * Higher-order component for adding error boundaries
 */
export function withErrorBoundary<P extends object>(
  Component: React.ComponentType<P>,
  errorBoundaryConfig?: Omit<ErrorBoundaryProps, 'children'>
) {
  const WrappedComponent = (props: P) => (
    <ErrorBoundary {...errorBoundaryConfig}>
      <Component {...props} />
    </ErrorBoundary>
  );

  WrappedComponent.displayName = `withErrorBoundary(${Component.displayName || Component.name})`;

  return WrappedComponent;
}

export default ErrorBoundary;