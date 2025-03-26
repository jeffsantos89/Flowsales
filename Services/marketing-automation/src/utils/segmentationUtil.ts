export const segmentLeads = (leads, criteria) => {
    return leads.filter(lead => criteria(lead));
  };
  