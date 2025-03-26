import 'cypress';

declare namespace Cypress {
  // @ts-expect-error - Augmenting Cypress namespace with custom commands
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  interface Chainable<Subject = unknown> {
    /**
     * Logs in a user with the given credentials.
     * @param credentials The user's credentials.
     * @returns The authentication token.
     */
    login(): Chainable<string>;
    /**
     * Logs out the current user.
     */
    logout(): void;
    /**
     * Sets the authentication token in localStorage.
     * @param token The authentication token.
     */
    setAuthToken(token: string): void;
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
    setCache(key: string, value: unknown): Chainable<void>;
    /**
     * Gets a value from the cache.
     * @param key The cache key.
     * @returns The cache value.
     */
    getCache(key: string): Chainable<unknown>;
    /**
     * Simulates a server error.
     */
    simulateServerError(): void;
  }
}
