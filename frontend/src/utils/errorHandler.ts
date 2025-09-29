/**
 * Error handling utilities for the HackSeek frontend application.
 */

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, any>;
}

export interface ApiErrorResponse {
  success: false;
  error: ApiError;
  request_id?: string;
  timestamp: number;
}

export interface ApiSuccessResponse<T = any> {
  success: true;
  data: T;
  message?: string;
  timestamp: number;
}

export type ApiResponse<T = any> = ApiSuccessResponse<T> | ApiErrorResponse;

/**
 * Custom error class for API errors
 */
export class HackSeekAPIError extends Error {
  public code: string;
  public details: Record<string, any>;
  public requestId?: string;
  public statusCode: number;

  constructor(
    message: string,
    code: string,
    statusCode: number,
    details: Record<string, any> = {},
    requestId?: string
  ) {
    super(message);
    this.name = 'HackSeekAPIError';
    this.code = code;
    this.details = details;
    this.requestId = requestId;
    this.statusCode = statusCode;
  }
}

/**
 * Network error class
 */
export class NetworkError extends Error {
  constructor(message: string = 'Network request failed') {
    super(message);
    this.name = 'NetworkError';
  }
}

/**
 * Timeout error class
 */
export class TimeoutError extends Error {
  constructor(message: string = 'Request timed out') {
    super(message);
    this.name = 'TimeoutError';
  }
}

/**
 * Handle API response and throw appropriate errors
 */
export function handleApiResponse<T>(response: Response, data: any): T {
  if (!response.ok) {
    // Try to extract error information from response
    if (data && typeof data === 'object' && !data.success) {
      const apiError = data as ApiErrorResponse;
      throw new HackSeekAPIError(
        apiError.error.message,
        apiError.error.code,
        response.status,
        apiError.error.details || {},
        apiError.request_id
      );
    }

    // Fallback to generic HTTP error
    throw new HackSeekAPIError(
      `HTTP ${response.status}: ${response.statusText}`,
      'HTTP_ERROR',
      response.status
    );
  }

  if (data && typeof data === 'object' && data.success === false) {
    const apiError = data as ApiErrorResponse;
    throw new HackSeekAPIError(
      apiError.error.message,
      apiError.error.code,
      response.status,
      apiError.error.details || {},
      apiError.request_id
    );
  }

  // Return the data portion of successful responses
  if (data && typeof data === 'object' && data.success === true) {
    return (data as ApiSuccessResponse<T>).data;
  }

  return data;
}

/**
 * Enhanced fetch with error handling and timeouts
 */
export async function apiRequest<T = any>(
  url: string,
  options: RequestInit & { timeout?: number } = {}
): Promise<T> {
  const { timeout = 30000, ...fetchOptions } = options;

  // Set default headers
  const headers = new Headers(fetchOptions.headers);
  if (!headers.has('Content-Type') && fetchOptions.body) {
    headers.set('Content-Type', 'application/json');
  }

  try {
    // Create timeout controller
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    const response = await fetch(url, {
      ...fetchOptions,
      headers,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    let data;
    try {
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        data = await response.json();
      } else {
        data = await response.text();
      }
    } catch (parseError) {
      throw new HackSeekAPIError(
        'Failed to parse response',
        'PARSE_ERROR',
        response.status
      );
    }

    return handleApiResponse<T>(response, data);

  } catch (error) {
    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        throw new TimeoutError();
      }

      if (error instanceof HackSeekAPIError) {
        throw error;
      }
    }

    throw new NetworkError(error instanceof Error ? error.message : 'Unknown network error');
  }
}

/**
 * Get user-friendly error message
 */
export function getErrorMessage(error: Error): string {
  if (error instanceof HackSeekAPIError) {
    // Return user-friendly messages for common error codes
    switch (error.code) {
      case 'VALIDATION_ERROR':
        return 'Please check your input and try again.';
      case 'AUTHENTICATION_ERROR':
        return 'Please log in to continue.';
      case 'AUTHORIZATION_ERROR':
        return 'You don\'t have permission to perform this action.';
      case 'NOT_FOUND_ERROR':
        return 'The requested resource was not found.';
      case 'RATE_LIMIT_ERROR':
        return 'Too many requests. Please wait a moment and try again.';
      case 'EXTERNAL_API_ERROR':
        return 'External service is currently unavailable. Please try again later.';
      case 'AI_SERVICE_ERROR':
        return 'AI service is temporarily unavailable. Please try again later.';
      case 'DATABASE_ERROR':
      case 'INTERNAL_ERROR':
        return 'A server error occurred. Please try again later.';
      default:
        return error.message;
    }
  }

  if (error instanceof NetworkError) {
    return 'Network connection failed. Please check your internet connection.';
  }

  if (error instanceof TimeoutError) {
    return 'Request timed out. Please try again.';
  }

  return error.message || 'An unexpected error occurred.';
}

/**
 * Log error to console and external service
 */
export function logError(
  error: Error,
  context?: {
    userId?: string;
    action?: string;
    component?: string;
    additionalData?: Record<string, any>;
  }
): void {
  const errorData = {
    name: error.name,
    message: error.message,
    stack: error.stack,
    timestamp: new Date().toISOString(),
    url: window.location.href,
    userAgent: navigator.userAgent,
    ...context,
  };

  // Log to console in development
  if (process.env.NODE_ENV === 'development') {
    console.error('Error logged:', errorData);
  }

  // TODO: Send to external logging service in production
  // Example: Sentry, LogRocket, etc.
}

/**
 * Error boundary helper function
 */
export function handleComponentError(
  error: Error,
  errorInfo: { componentStack: string },
  componentName: string
): void {
  logError(error, {
    component: componentName,
    additionalData: {
      componentStack: errorInfo.componentStack,
    },
  });
}

/**
 * Retry function with exponential backoff
 */
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  baseDelay: number = 1000
): Promise<T> {
  let lastError: Error;

  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error as Error;

      // Don't retry for certain error types
      if (error instanceof HackSeekAPIError) {
        if (['VALIDATION_ERROR', 'AUTHENTICATION_ERROR', 'AUTHORIZATION_ERROR'].includes(error.code)) {
          throw error;
        }
      }

      if (i < maxRetries - 1) {
        // Calculate delay with exponential backoff and jitter
        const delay = baseDelay * Math.pow(2, i) + Math.random() * 1000;
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }

  throw lastError!;
}

/**
 * Format validation errors for display
 */
export function formatValidationErrors(details: Record<string, any>): string[] {
  const errors: string[] = [];

  if (details.field && details.issue) {
    errors.push(`${details.field}: ${details.issue}`);
  } else if (Array.isArray(details.errors)) {
    details.errors.forEach((err: any) => {
      if (typeof err === 'string') {
        errors.push(err);
      } else if (err.field && err.message) {
        errors.push(`${err.field}: ${err.message}`);
      }
    });
  } else {
    // Try to extract error messages from nested objects
    Object.entries(details).forEach(([key, value]) => {
      if (typeof value === 'string') {
        errors.push(`${key}: ${value}`);
      } else if (Array.isArray(value)) {
        value.forEach((msg) => {
          if (typeof msg === 'string') {
            errors.push(`${key}: ${msg}`);
          }
        });
      }
    });
  }

  return errors.length > 0 ? errors : ['Validation failed'];
}