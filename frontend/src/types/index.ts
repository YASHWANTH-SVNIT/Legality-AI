export interface RiskyClause {
  chunk_id: string;
  category: string;
  original_text: string;
  risk_score: number;
  risk_level: string;
  pessimist_analysis: string;
  optimist_analysis: string;
  arbiter_reasoning: string;
  suggested_fix: string;
  fix_comment: string;
  key_changes: string[];
}

export interface CompoundRisk {
  risk_type: string;
  severity: string;
  description: string;
  affected_clauses: string[];
  mitigation: string;
  risk_score: number;
}

export interface AnalysisResults {
  document: {
    filename: string;
    total_chunks: number;
    risky_clauses_found: number;
  };
  summary: {
    overall_risk: string;
    average_risk_score: number;
    compound_risks_found: number;
    categories_flagged: string[];
  };
  risky_clauses: RiskyClause[];
  compound_risks: CompoundRisk[];
}

export interface AnalysisStatus {
  analysis_id: string;
  status: 'processing' | 'completed' | 'failed';
  filename: string;
  progress: number;
}