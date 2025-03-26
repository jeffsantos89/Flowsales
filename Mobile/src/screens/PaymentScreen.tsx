import React, { useState, useCallback } from 'react';
import { View, Text, TextInput, Button, StyleSheet, ActivityIndicator, ScrollView, Alert } from 'react-native';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '../store';
import { formatCurrency } from '../utils/helpers';
import { useNavigation } from '@react-navigation/native';
import { usePayment } from '../hooks/usePayment';
import { CardItem } from '../types/cart.ts';
import { validateCard, validateExpiry, validateCVV, validateName } from '../utils/validations';
import { CustomTextInput } from '../components/CustomTextInput';
import { PaymentButton } from '../components/PaymentButton';
import { theme } from '../theme';

interface PaymentScreenProps {
  route?: {
    params?: {
      redirectTo?: string;
    };
  };
}

export default function PaymentScreen({ route }: PaymentScreenProps) {
  const [paymentForm, setPaymentForm] = useState({
    cardNumber: '',
    cvv: '',
    expire: '',
    holderName: '',
  });
  const [errors, setErrors] = useState({
    cardNumber: '',
    cvv: '',
    expire: '',
    holderName: '',
  });
  const [loading, setLoading] = useState(false);

  const dispatch = useDispatch<AppDispatch>();
  const navigation = useNavigation();
  const cartItems = useSelector((state: RootState) => state.cart.items as CardItem[]);

  const totalValue = useMemo(() => 
    cartItems.reduce((total, item) => total + item.price * item.quantity, 0),
    [cartItems]
  );

  const updateFormField = useCallback((field: keyof typeof paymentForm) => (value: string) => {
    setPaymentForm(prev => ({ ...prev, [field]: value }));
    setErrors(prev => ({ ...prev, [field]: '' }));
  }, []);

  const validateForm = useCallback((): boolean => {
    const newErrors = {
      cardNumber: validateCard(paymentForm.cardNumber),
      cvv: validateCVV(paymentForm.cvv),
      expire: validateExpiry(paymentForm.expire),
      holderName: validateName(paymentForm.holderName),
    };

    setErrors(newErrors);
    return !Object.values(newErrors).some(error => error !== '');
  }, [paymentForm]);

  const { handlePayment: processPayment } = usePayment({
    ...paymentForm,
    cartItems,
    totalValue,
    setLoading,
    dispatch,
    navigation,
  });

  const handlePayment = useCallback(async () => {
    try {
      if (!validateForm()) {
        Alert.alert('Erro', 'Por favor, corrija os campos com erro.');
        return;
      }

      if (cartItems.length === 0) {
        Alert.alert('Erro', 'Seu carrinho está vazio.');
        return;
      }

      await processPayment();
    } catch (error) {
      Alert.alert('Erro', 'Ocorreu um erro ao processar o pagamento.');
      setLoading(false);
    }
  }, [paymentForm, cartItems, processPayment, validateForm]);

  const formatCardNumber = useCallback((value: string) => {
    return value
      .replace(/\s/g, '')
      .replace(/(\d{4})/g, '$1 ')
      .trim();
  }, []);

  const formatExpiry = useCallback((value: string) => {
    return value
      .replace(/\D/g, '')
      .replace(/(\d{2})(\d)/, '$1/$2')
      .substr(0, 5);
  }, []);

  return (
    <ScrollView style={styles.container} keyboardShouldPersistTaps="handled">
      <Text style={styles.title}>Pagamento</Text>

      <CustomTextInput
        label="Número do Cartão"
        value={paymentForm.cardNumber}
        onChangeText={(value) => updateFormField('cardNumber')(formatCardNumber(value))}
        placeholder="0000 0000 0000 0000"
        keyboardType="numeric"
        maxLength={19}
        error={errors.cardNumber}
      />

      <View style={styles.row}>
        <View style={styles.halfWidth}>
          <CustomTextInput
            label="Validade"
            value={paymentForm.expire}
            onChangeText={(value) => updateFormField('expire')(formatExpiry(value))}
            placeholder="MM/YY"
            keyboardType="numeric"
            maxLength={5}
            error={errors.expire}
          />
        </View>

        <View style={styles.halfWidth}>
          <CustomTextInput
            label="CVV"
            value={paymentForm.cvv}
            onChangeText={updateFormField('cvv')}
            placeholder="123"
            keyboardType="numeric"
            secureTextEntry
            maxLength={3}
            error={errors.cvv}
          />
        </View>
      </View>

      <CustomTextInput
        label="Nome do Titular"
        value={paymentForm.holderName}
        onChangeText={updateFormField('holderName')}
        placeholder="Nome como está no cartão"
        autoCapitalize="characters"
        error={errors.holderName}
      />

      <Text style={styles.total}>Total: {formatCurrency(totalValue)}</Text>

      <PaymentButton
        loading={loading}
        onPress={handlePayment}
        totalValue={totalValue}
      />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: theme.spacing.large,
    backgroundColor: theme.colors.background,
  },
  title: {
    fontSize: theme.typography.sizes.large,
    marginBottom: theme.spacing.medium,
    textAlign: 'center',
    color: theme.colors.primary,
    fontFamily: theme.typography.fontFamily.bold,
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: theme.spacing.small,
  },
  halfWidth: {
    flex: 1,
  },
  total: {
    marginVertical: theme.spacing.medium,
    fontSize: theme.typography.sizes.medium,
    textAlign: 'center',
    fontFamily: theme.typography.fontFamily.semiBold,
    color: theme.colors.text,
  },
});
