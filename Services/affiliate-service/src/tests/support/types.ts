/// <reference types="cypress" />

// Define a type for API responses
export interface ApiResponse<T> {
  data: T | null;
  error: string | null;
  status: number;
  headers: Record<string, string>;
}

// Define a type for authentication tokens
export interface AuthToken {
  token: string;
  expiresAt?: Date;
  refreshToken?: string;
}

// Define a type for user credentials
export interface UserCredentials {
  email: string;
  password: string;
}

// Define a type for cache entries
export interface CacheEntry<T> {
  key: string;
  value: T;
  expiresAt?: Date;
}

// Define a type for server error configurations
export interface ServerErrorConfig {
  method?: string;
  url?: string;
  status?: number;
  response?: unknown;
}

// Define a type for affiliate data
export interface Affiliate {
  id: string;
  name: string;
  email: string;
  createdAt: string;
  updatedAt: string;
  // Add other affiliate properties here
}

// Define a type for commission data
export interface Commission {
  id: string;
  amount: number;
  status: 'pending' | 'approved' | 'rejected';
  affiliateId: string;
  createdAt: string;
  updatedAt: string;
  // Add other commission properties here
}

// Define a type for dashboard data
export interface DashboardData {
  totalAffiliates: number;
  totalCommissions: number;
  totalEarnings: number;
  // Add other dashboard properties here
}

// Define a type for pagination options
export interface PaginationOptions {
  page: number;
  limit: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

// Define a type for filter options
export interface FilterOptions<T> {
  [key: string]: T;
}

// Define a type for API request options
export interface ApiRequestOptions {
  method: string;
  url: string;
  body?: unknown;
  headers?: Record<string, string>;
  failOnStatusCode?: boolean;
}

declare global {
  namespace Cypress {
  interface Chainable<Subject = unknown> {
    /**
     * Logs in a user with the given credentials.
     * @param credentials The user's credentials.
     * @returns The authentication token.
     */
    login(credentials?: UserCredentials): Chainable<AuthToken>;
    /**
     * Logs out the current user.
     */
    logout(): Chainable<void>;
    /**
     * Sets the authentication token.
     * @param token The authentication token.
     */
    setAuthToken(token: AuthToken): Chainable<void>;
    /**
     * Checks if the user is authenticated.
     * @returns True if the user is authenticated, false otherwise.
     */
    isAuthenticated(): Chainable<boolean>;

    /**
     * Clears the cache.
     */
    clearCache(): Chainable<void>;
    /**
     * Sets a value in the cache.
     * @param key The cache key.
     * @param value The cache value.
     */
    setCache<T>(key: string, value: T): Chainable<void>;
    /**
     * Gets a value from the cache.
     * @param key The cache key.
     * @returns The cache value.
     */
    getCache<T>(key: string): Chainable<T | null>;

    /**
     * Makes a request to the API.
     * @param options The API request options.
     * @returns The API response.
     */
    apiRequest<T>(options: ApiRequestOptions): Chainable<ApiResponse<T>>;

    /**
     * Simulates a server error.
     * @param config The server error configuration.
     */
    simulateServerError(config?: ServerErrorConfig): Chainable<void>;

    /**
     * Gets a list of affiliates.
     * @param options The pagination and filter options.
     * @returns The list of affiliates.
     */
    getAffiliates(
      options?: PaginationOptions & FilterOptions<string>
    ): Chainable<Affiliate[]>;
    /**
     * Gets a list of commissions.
     * @param options The pagination and filter options.
     * @returns The list of commissions.
     */
    getCommissions(
      options?: PaginationOptions & FilterOptions<string>
    ): Chainable<Commission[]>;
    /**
     * Gets the dashboard data.
     * @returns The dashboard data.
     */
    getDashboardData(): Chainable<DashboardData>;

    /**
     * Clears the local storage.
     */
    clearLocalStorage(): Chainable<void>;
    /**
     * Logs a message to the console.
     * @param message The message to log.
     */
    log(message: string): Chainable<void>;

    // Example: A command that always returns a string
    getString(): Chainable<string>;
    // ... your custom command definitions ...
  }
}

export {};