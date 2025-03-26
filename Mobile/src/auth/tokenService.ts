import axios from 'axios';
import * as SecureStore from 'expo-secure-store';
import { API_URL } from '../services/config';

const ACCESS_KEY = 'store_access_token';
const REFRESH_KEY = 'store_refresh_token';

interface Tokens {
  accessToken: string;
  refreshToken: string;
}

interface UserData {
  // Defina aqui os campos esperados em userData
}

interface LoginResponse {
  userData: UserData;
  tokens: Tokens;
}

async function saveTokens(tokens: Tokens): Promise<void> {
  const { accessToken, refreshToken } = tokens;
  await SecureStore.setItemAsync(ACCESS_KEY, accessToken);
  await SecureStore.setItemAsync(REFRESH_KEY, refreshToken);
}

async function getStoredToken(key: string): Promise<string | null> {
  try {
    return await SecureStore.getItemAsync(key);
  } catch (error) {
    console.error(`Error getting token from SecureStore: ${error}`);
    return null;
  }
}

export async function loginService(email: string, password: string): Promise<LoginResponse> {
  try {
    const { data } = await axios.post(`${API_URL}/auth/login`, { email, password });
    const { accessToken, refreshToken, userData } = data;

    await saveTokens({ accessToken, refreshToken });

    return { userData, tokens: { accessToken, refreshToken } };
  } catch (error) {
    console.error(`Login service error: ${error}`);
    throw new Error('Failed to login');
  }
}

export async function refreshService(): Promise<Tokens> {
  try {
    const oldRefresh = await getStoredToken(REFRESH_KEY);
    if (!oldRefresh) throw new Error('No refresh token found');

    const { data } = await axios.post(`${API_URL}/auth/refresh`, { refreshToken: oldRefresh });
    const { accessToken: newAccess, refreshToken: newRefresh } = data;

    await saveTokens({ accessToken: newAccess, refreshToken: newRefresh });

    return { accessToken: newAccess, refreshToken: newRefresh };
  } catch (error) {
    console.error(`Refresh service error: ${error}`);
    throw new Error('Failed to refresh token');
  }
}

export async function logoutService(): Promise<void> {
  try {
    await SecureStore.deleteItemAsync(ACCESS_KEY);
    await SecureStore.deleteItemAsync(REFRESH_KEY);
  } catch (error) {
    console.error(`Logout service error: ${error}`);
    throw new Error('Failed to logout');
  }
}

export async function getTokens(): Promise<Tokens | null> {
  try {
    const accessToken = await getStoredToken(ACCESS_KEY);
    const refreshToken = await getStoredToken(REFRESH_KEY);

    if (!accessToken || !refreshToken) {
      return null;
    }

    return { accessToken, refreshToken };
  } catch (error) {
    console.error(`Get tokens error: ${error}`);
    return null;
  }
}
