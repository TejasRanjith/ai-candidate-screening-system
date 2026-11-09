import {
  RoleItem,
  SampleResume,
  SessionStartResponse,
  TurnQuestionResponse,
  AnswerEvaluationResponse,
  FinalReportResponse
} from '../types';

const API_BASE = '/api';

export const api = {
  async getRoles(): Promise<RoleItem[]> {
    const res = await fetch(`${API_BASE}/roles`);
    if (!res.ok) throw new Error('Failed to fetch available roles');
    const data = await res.json();
    return data.roles;
  },

  async getSampleResumes(): Promise<SampleResume[]> {
    const res = await fetch(`${API_BASE}/sample-resumes`);
    if (!res.ok) throw new Error('Failed to fetch sample resumes');
    const data = await res.json();
    return data.samples;
  },

  async startSessionWithFile(file: File, role: string): Promise<SessionStartResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('role', role);

    const res = await fetch(`${API_BASE}/sessions/start`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to start interview session' }));
      throw new Error(err.detail || 'Failed to start interview session');
    }
    return res.json();
  },

  async startSessionWithSample(sampleId: string, role: string): Promise<SessionStartResponse> {
    const formData = new FormData();
    formData.append('sample_resume_id', sampleId);
    formData.append('role', role);

    const res = await fetch(`${API_BASE}/sessions/start`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to start interview session' }));
      throw new Error(err.detail || 'Failed to start interview session');
    }
    return res.json();
  },

  async getNextQuestion(sessionId: string): Promise<TurnQuestionResponse> {
    const res = await fetch(`${API_BASE}/sessions/${sessionId}/next-question`);
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to retrieve next question' }));
      throw new Error(err.detail || 'Failed to retrieve next question');
    }
    return res.json();
  },

  async submitAnswer(sessionId: string, answer: string): Promise<AnswerEvaluationResponse> {
    const res = await fetch(`${API_BASE}/sessions/${sessionId}/submit-answer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ answer }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to submit answer' }));
      throw new Error(err.detail || 'Failed to submit answer');
    }
    return res.json();
  },

  async getReport(sessionId: string): Promise<FinalReportResponse> {
    const res = await fetch(`${API_BASE}/sessions/${sessionId}/report`);
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to fetch interview report' }));
      throw new Error(err.detail || 'Failed to fetch interview report');
    }
    return res.json();
  }
};
