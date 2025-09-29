/**
 * Health check page for monitoring frontend and backend status.
 */
import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { apiRequest } from '../utils/errorHandler';

interface HealthStatus {
  status: string;
  version: string;
  timestamp: string;
  uptime: number;
  environment: string;
  response_time_ms: number;
  services: {
    [key: string]: {
      status: string;
      type?: string;
      response_time_ms?: number;
      error?: string;
    };
  };
  unhealthy_services?: string[];
}

interface HealthResponse {
  success: boolean;
  data: HealthStatus;
  timestamp: string;
}

const HealthPage: React.FC = () => {
  const [backendHealth, setBackendHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastChecked, setLastChecked] = useState<Date | null>(null);

  const checkBackendHealth = async () => {
    try {
      setError(null);
      const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await apiRequest<HealthStatus>(`${apiBaseUrl}/health`);
      setBackendHealth(response);
      setLastChecked(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to check backend health');
      setBackendHealth(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkBackendHealth();

    // Auto-refresh every 30 seconds
    const interval = setInterval(checkBackendHealth, 30000);

    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'text-green-600 bg-green-100';
      case 'degraded':
        return 'text-yellow-600 bg-yellow-100';
      case 'unhealthy':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const formatUptime = (seconds: number) => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);

    if (days > 0) {
      return `${days}d ${hours}h ${minutes}m`;
    }
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <Head>
        <title>Health Check - HackSeek</title>
        <meta name="description" content="HackSeek system health status" />
      </Head>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">System Health</h1>
          <p className="text-gray-600 mt-2">
            Monitor the status of HackSeek services and components
          </p>
          {lastChecked && (
            <p className="text-sm text-gray-500 mt-1">
              Last checked: {lastChecked.toLocaleString()}
            </p>
          )}
        </div>

        {/* Frontend Status */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="px-6 py-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">Frontend</h2>
              <span className="px-3 py-1 rounded-full text-sm font-medium text-green-600 bg-green-100">
                Healthy
              </span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-gray-500">Status</p>
                <p className="font-medium">Running</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Version</p>
                <p className="font-medium">1.0.0</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Framework</p>
                <p className="font-medium">Next.js</p>
              </div>
            </div>
          </div>
        </div>

        {/* Backend Status */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="px-6 py-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">Backend API</h2>
              <div className="flex items-center space-x-2">
                {loading ? (
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
                ) : (
                  <>
                    {backendHealth && (
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(backendHealth.status)}`}>
                        {backendHealth.status.charAt(0).toUpperCase() + backendHealth.status.slice(1)}
                      </span>
                    )}
                    <button
                      onClick={checkBackendHealth}
                      className="px-3 py-1 text-sm text-blue-600 hover:text-blue-800"
                    >
                      Refresh
                    </button>
                  </>
                )}
              </div>
            </div>

            {error && (
              <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
                <p className="text-red-600 text-sm">
                  <strong>Error:</strong> {error}
                </p>
              </div>
            )}

            {backendHealth && (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                  <div>
                    <p className="text-sm text-gray-500">Version</p>
                    <p className="font-medium">{backendHealth.version}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Environment</p>
                    <p className="font-medium">{backendHealth.environment}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Uptime</p>
                    <p className="font-medium">{formatUptime(backendHealth.uptime)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Response Time</p>
                    <p className="font-medium">{backendHealth.response_time_ms}ms</p>
                  </div>
                </div>

                {/* Services Status */}
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-3">Services</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {Object.entries(backendHealth.services).map(([name, service]) => (
                      <div key={name} className="border border-gray-200 rounded-md p-4">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium text-gray-900 capitalize">{name}</h4>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(service.status)}`}>
                            {service.status}
                          </span>
                        </div>
                        {service.type && (
                          <p className="text-sm text-gray-500">Type: {service.type}</p>
                        )}
                        {service.response_time_ms !== undefined && (
                          <p className="text-sm text-gray-500">Response: {service.response_time_ms}ms</p>
                        )}
                        {service.error && (
                          <p className="text-sm text-red-600 mt-2">Error: {service.error}</p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {backendHealth.unhealthy_services && backendHealth.unhealthy_services.length > 0 && (
                  <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-md">
                    <h4 className="text-sm font-medium text-yellow-800 mb-2">
                      Unhealthy Services
                    </h4>
                    <ul className="text-sm text-yellow-700">
                      {backendHealth.unhealthy_services.map(service => (
                        <li key={service} className="capitalize">• {service}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </>
            )}
          </div>
        </div>

        {/* System Information */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">System Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Frontend URL</p>
                <p className="font-medium">{window.location.origin}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">API URL</p>
                <p className="font-medium">
                  {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Environment</p>
                <p className="font-medium">{process.env.NODE_ENV}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Build Time</p>
                <p className="font-medium">{new Date().toISOString()}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HealthPage;