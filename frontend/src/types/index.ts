export interface RoleItem {
  id: string;
  title: string;
  description: string;
  corpus_source: string;
}

export interface SampleResume {
  id: string;
  name: string;
  role: string;
  experience_level: string;
  skills: string[];
  summary: string;
}

export interface SessionStartResponse {
  session_id: string;
  candidate_name: string;
  target_role: string;
  experience_level: string;
  parsed_skills: string[];
  domain_exposure: string[];
  project_highlights: string[];
  raw_summary?: string;
  total_turns: number;
  current_turn_index: number;
  status: string;
}

export interface TurnQuestionResponse {
  session_id: string;
  turn_index: number;
  total_turns: number;
  question_text: string;
  targeted_skill: string;
  source_topic: string;
  cited_concept: string;
  retrieved_context_preview?: string;
  status: string;
}

export interface AnswerEvaluationResponse {
  session_id: string;
  turn_index: number;
  total_turns: number;
  score: number;
  technical_accuracy: string;
  strengths: string[];
  missing_points: string[];
  constructive_feedback: string;
  model_answer_summary: string;
  is_completed: boolean;
  next_turn_index?: number;
}

export interface TurnReportItem {
  turn_index: number;
  targeted_skill: string;
  source_topic: string;
  cited_concept: string;
  question_text: string;
  candidate_answer?: string;
  score?: number;
  technical_accuracy?: string;
  strengths: string[];
  missing_points: string[];
  constructive_feedback?: string;
  model_answer_summary?: string;
  retrieved_chunks_preview: Array<{
    text: string;
    book: string;
    chapter: string;
    source: string;
    distance?: number;
  }>;
}

export interface FinalReportResponse {
  session_id: string;
  candidate_name: string;
  target_role: string;
  experience_level: string;
  overall_score: number;
  performance_tier: string;
  total_turns: number;
  completed_turns: number;
  status: string;
  created_at: string;
  summary: string;
  strengths: string[];
  areas_for_improvement: string[];
  hiring_recommendation: string;
  turns: TurnReportItem[];
}
