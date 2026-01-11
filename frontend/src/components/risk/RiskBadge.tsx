import React from 'react';
import { getRiskColor } from '../../utils/colors';

interface RiskBadgeProps {
  riskLevel: string;
  score: number;
}

const RiskBadge: React.FC<RiskBadgeProps> = ({ riskLevel, score }) => {
  return (
    <div className="flex items-center gap-2">
      <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getRiskColor(riskLevel)}`}>
        {riskLevel}
      </span>
      <span className="text-gray-600 font-medium">{score}/100</span>
    </div>
  );
};

export default RiskBadge;