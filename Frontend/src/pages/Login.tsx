import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Formik, Form, Field, FormikHelpers } from 'formik';
import * as Yup from 'yup';
import { toast } from 'react-toastify';
import styled from 'styled-components';
import { useAuth } from '../auth/AuthProvider';
import { loginService } from '../services/authService';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { ErrorBoundary } from '../components/common/ErrorBoundary';

// Types
interface LoginFormValues {
  email: string;
  cpfCnpj: string;
  name: string;
  acceptedTerms: boolean;
}

// Styled components with theme support
const StyledContainer = styled.div`
  max-width: 450px;
  margin: 2rem auto;
  padding: 2.5rem;
  box-shadow: ${({ theme }) => theme.shadows.card};
  border-radius: ${({ theme }) => theme.borderRadius.lg};
  background: ${({ theme }) => theme.colors.background};
`;

const FormGroup = styled.div`
  margin-bottom: 1.5rem;
  position: relative;
`;

const StyledField = styled(Field)`
  width: 100%;
  padding: 0.75rem;
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: ${({ theme }) => theme.borderRadius.md};
  transition: all 0.2s ease-in-out;
  
  &:focus {
    border-color: ${({ theme }) => theme.colors.primary};
    box-shadow: 0 0 0 2px ${({ theme }) => theme.colors.primaryLight};
    outline: none;
  }
`;

const ErrorMessage = styled.div`
  color: ${({ theme }) => theme.colors.error};
  font-size: 0.875rem;
  margin-top: 0.25rem;
`;

// Validation schema with custom error messages
const LoginSchema = Yup.object().shape({
  email: Yup.string()
    .email('Por favor, insira um email válido')
    .required('Email é obrigatório')
    .trim(),
  cpfCnpj: Yup.string()
    .required('CPF/CNPJ é obrigatório')
    .min(11, 'CPF/CNPJ deve ter no mínimo 11 dígitos')
    .max(14, 'CPF/CNPJ deve ter no máximo 14 dígitos')
    .matches(/^\d+$/, 'CPF/CNPJ deve conter apenas números'),
  name: Yup.string()
    .required('Nome é obrigatório')
    .min(3, 'Nome deve ter pelo menos 3 caracteres')
    .max(100, 'Nome muito longo')
    .trim(),
  acceptedTerms: Yup.boolean()
    .oneOf([true], 'Você precisa aceitar os termos para continuar')
});

const Login: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = async (
    values: LoginFormValues,
    { setSubmitting, setErrors }: FormikHelpers<LoginFormValues>
  ) => {
    try {
      // Get IP address
      const ipResponse = await fetch('https://api.ipify.org?format=json');
      const { ip } = await ipResponse.json();

      // Attempt login
      const response = await loginService.register({
        ...values,
        purposes: ['marketing'],
        ip
      });

      const { token, user } = response.data;

      // Store user data securely
      login(token);
      localStorage.setItem('user', JSON.stringify(user));

      toast.success('Login realizado com sucesso!');
      navigate('/dashboard');
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Erro ao realizar login';
      toast.error(errorMessage);
      setErrors({ email: errorMessage });
    } finally {
      setSubmitting(false);
    }
  };

  const initialValues: LoginFormValues = {
    email: '',
    cpfCnpj: '',
    name: '',
    acceptedTerms: false
  };

  return (
    <ErrorBoundary>
      <StyledContainer>
        <h1 className="text-2xl font-bold mb-6">Login / Registro</h1>
        
        <Formik
          initialValues={initialValues}
          validationSchema={LoginSchema}
          onSubmit={handleSubmit}
        >
          {({ errors, touched, isSubmitting }) => (
            <Form className="space-y-4">
              <FormGroup>
                <StyledField
                  name="name"
                  type="text"
                  placeholder="Nome completo"
                  autoComplete="name"
                />
                {errors.name && touched.name && (
                  <ErrorMessage>{errors.name}</ErrorMessage>
                )}
              </FormGroup>

              <FormGroup>
                <StyledField
                  name="email"
                  type="email"
                  placeholder="Email"
                  autoComplete="email"
                />
                {errors.email && touched.email && (
                  <ErrorMessage>{errors.email}</ErrorMessage>
                )}
              </FormGroup>

              <FormGroup>
                <StyledField
                  name="cpfCnpj"
                  type="text"
                  placeholder="CPF ou CNPJ"
                  maxLength={14}
                />
                {errors.cpfCnpj && touched.cpfCnpj && (
                  <ErrorMessage>{errors.cpfCnpj}</ErrorMessage>
                )}
              </FormGroup>

              <FormGroup>
                <label className="flex items-center space-x-2">
                  <Field
                    type="checkbox"
                    name="acceptedTerms"
                    className="form-checkbox"
                  />
                  <span className="text-sm">
                    Li e aceito os{' '}
                    <a href="/terms" className="text-blue-600 hover:underline">
                      termos da LGPD
                    </a>
                  </span>
                </label>
                {errors.acceptedTerms && touched.acceptedTerms && (
                  <ErrorMessage>{errors.acceptedTerms}</ErrorMessage>
                )}
              </FormGroup>

              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full bg-blue-600 text-white p-3 rounded-lg hover:bg-blue-700 
                         disabled:opacity-50 transition-colors duration-200 flex items-center justify-center"
              >
                {isSubmitting ? <LoadingSpinner /> : 'Entrar'}
              </button>
            </Form>
          )}
        </Formik>
      </StyledContainer>
    </ErrorBoundary>
  );
};

export default Login;
