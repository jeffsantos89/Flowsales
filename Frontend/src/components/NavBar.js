import React, { useContext, memo } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { AuthContext } from '../auth/AuthProvider';
import styled from 'styled-components';

const StyledNav = styled.nav`
  background: #ffffff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  padding: 1rem 2rem;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
`;

const NavLink = styled(Link)`
  color: #333;
  text-decoration: none;
  padding: 0.5rem 1rem;
  margin: 0 0.5rem;
  border-radius: 4px;
  transition: all 0.3s ease;

  &:hover {
    background: #f0f0f0;
  }

  &.active {
    background: #007bff;
    color: white;
  }
`;

const LogoutButton = styled.button`
  background: #dc3545;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    background: #c82333;
  }
`;

const NavContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const NavBar = () => {
  const { isAuthenticated, logout, user } = useContext(AuthContext);
  const location = useLocation();

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Erro ao fazer logout:', error);
    }
  };

  const isActiveRoute = (path) => {
    return location.pathname === path;
  };

  const navLinks = {
    public: [
      { to: '/', label: 'Home' }
    ],
    private: [
      { to: '/dashboard', label: 'Dashboard' },
      { to: '/products', label: 'Produtos' },
      { to: '/cart', label: 'Carrinho' },
      { to: '/checkout', label: 'Checkout' }
    ]
  };

  return (
    <StyledNav>
      <NavContainer>
        <div>
          {navLinks.public.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={isActiveRoute(link.to) ? 'active' : ''}
            >
              {link.label}
            </NavLink>
          ))}

          {isAuthenticated && (
            <>
              {navLinks.private.map((link) => (
                <NavLink
                  key={link.to}
                  to={link.to}
                  className={isActiveRoute(link.to) ? 'active' : ''}
                >
                  {link.label}
                </NavLink>
              ))}
            </>
          )}
        </div>

        <div>
          {isAuthenticated ? (
            <>
              <span>Olá, {user?.name || 'Usuário'}</span>
              <LogoutButton onClick={handleLogout}>Sair</LogoutButton>
            </>
          ) : (
            <NavLink to="/login" className={isActiveRoute('/login') ? 'active' : ''}>
              Login
            </NavLink>
          )}
        </div>
      </NavContainer>
    </StyledNav>
  );
};

export default memo(NavBar);
