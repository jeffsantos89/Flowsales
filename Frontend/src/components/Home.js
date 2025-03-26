import React from 'react';
import { Link } from 'react-router-dom';
import PropTypes from 'prop-types';

const Home = () => {
  const navLinks = [
    { path: '/login', label: 'Login' },
    { path: '/dashboard', label: 'Dashboard' },
    { path: '/products', label: 'Produtos' },
    { path: '/cart', label: 'Carrinho' },
    { path: '/checkout', label: 'Checkout' },
  ];

  return (
    <div style={{ margin: '20px' }}>
      <h2>Bem-vindo à Home</h2>
      <nav>
        {navLinks.map((link, index) => (
          <React.Fragment key={index}>
            <Link to={link.path}>{link.label}</Link>
            {index < navLinks.length - 1 && ' | '}
          </React.Fragment>
        ))}
      </nav>
    </div>
  );
};

Home.propTypes = {
  navLinks: PropTypes.arrayOf(
    PropTypes.shape({
      path: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
    })
  ),
};

export default Home;