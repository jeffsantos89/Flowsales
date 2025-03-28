const tenantPolicies = {
  'flowsale': {
    requireMFA: true,
    allowedCountries: ['BR'],
    maxSessions: 1
  },
  'partnerA': {
    requireMFA: false,
    allowedCountries: ['BR', 'US'],
    maxSessions: 3
  }
};

export const getPolicyForTenant = (tenant: string) => {
  return tenantPolicies[tenant] || tenantPolicies['flowsale'];
};
