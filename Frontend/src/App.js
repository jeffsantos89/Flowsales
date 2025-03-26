// src/components/PrivateRoute.js
import React, { useContext } from 'react';
import { Route, Navigate } from 'react-router-dom';
import { AuthContext } from '../auth/AuthProvider';

const PrivateRoute = ({ element: Component, ...rest }) => {
  const { isAuthenticated } = useContext(AuthContext);

  return (
    <Route
      {...rest}
      element={isAuthenticated ? <Component /> : <Navigate to="/login" />}
    />
  );
};

export default PrivateRoute;
