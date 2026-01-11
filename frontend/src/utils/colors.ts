export const getRiskColor = (riskLevel: string): string => {
  switch (riskLevel.toLowerCase()) {
    case 'critical':
      return 'bg-critical text-white';
    case 'high':
      return 'bg-high text-white';
    case 'medium':
      return 'bg-medium text-white';
    case 'low':
      return 'bg-low text-white';
    default:
      return 'bg-gray-500 text-white';
  }
};

export const getRiskBorderColor = (riskLevel: string): string => {
  switch (riskLevel.toLowerCase()) {
    case 'critical':
      return 'border-critical';
    case 'high':
      return 'border-high';
    case 'medium':
      return 'border-medium';
    case 'low':
      return 'border-low';
    default:
      return 'border-gray-500';
  }
};

export const getRiskTextColor = (riskLevel: string): string => {
  switch (riskLevel.toLowerCase()) {
    case 'critical':
      return 'text-critical';
    case 'high':
      return 'text-high';
    case 'medium':
      return 'text-medium';
    case 'low':
      return 'text-low';
    default:
      return 'text-gray-500';
  }
};