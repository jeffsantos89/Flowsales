import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { loginService, refreshService, logoutService } from '../../auth/tokenService';

interface AuthState {
  isAuthenticated: boolean;
  user: { name: string; email: string } | null;
}

const initialState: AuthState = {
  isAuthenticated: false,
  user: null
};

// Thunk: login
export const loginThunk = createAsyncThunk(
  'auth/login',
  async ({ email, password }: { email: string; password: string }) => {
    const result = await loginService(email, password);
    // result { userData, tokens } 
    return result;
  }
);

// Thunk: logout
export const logoutThunk = createAsyncThunk('auth/logout', async () => {
  await logoutService();
});

// Thunk: refresh
export const refreshThunk = createAsyncThunk('auth/refresh', async () => {
  const newTokens = await refreshService();
  return newTokens; // { accessToken, refreshToken }
});

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setUnauthenticated: (state) => {
      state.isAuthenticated = false;
      state.user = null;
    },
    login: (state) => {
      state.isAuthenticated = true;
    },
    logout: (state) => {
      state.isAuthenticated = false;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(loginThunk.fulfilled, (state, action: PayloadAction<any>) => {
        state.isAuthenticated = true;
        state.user = action.payload.userData;
      })
      .addCase(loginThunk.rejected, (state) => {
        state.isAuthenticated = false;
        state.user = null;
      })
      .addCase(logoutThunk.fulfilled, (state) => {
        state.isAuthenticated = false;
        state.user = null;
      })
      .addCase(refreshThunk.fulfilled, (state) => {
        state.isAuthenticated = true;
      })
      .addCase(refreshThunk.rejected, (state) => {
        state.isAuthenticated = false;
        state.user = null;
      });
  }
});

export const { setUnauthenticated, login, logout } = authSlice.actions;
export default authSlice.reducer;

// import { isEmailValid } from '../utils/helpers'; // Ensure this module exists and is correctly named



// "R$ 29,90"

const isValidEmail = isEmailValid('exemplo@teste.com');
if (!isValidEmail) {
  alert('Email inválido!');
}

function alert(arg0: string) {
    throw new Error('Function not implemented.');
}

function isEmailValid(email: string): boolean {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

