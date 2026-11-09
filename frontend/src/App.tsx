import { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { Stepper } from './components/Stepper';
import { ResumeUploadStep } from './components/ResumeUploadStep';
import { ProfileReviewStep } from './components/ProfileReviewStep';
import { InterviewRoomStep } from './components/InterviewRoomStep';
import { ReportStep } from './components/ReportStep';
import { api } from './services/api';
import {
  RoleItem,
  SampleResume,
  SessionStartResponse,
  TurnQuestionResponse,
  AnswerEvaluationResponse,
  FinalReportResponse
} from './types';

export function App() {
  const [currentStep, setCurrentStep] = useState<number>(1);
  const [roles, setRoles] = useState<RoleItem[]>([]);
  const [sampleResumes, setSampleResumes] = useState<SampleResume[]>([]);
  const [session, setSession] = useState<SessionStartResponse | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<TurnQuestionResponse | null>(null);
  const [activeFeedback, setActiveFeedback] = useState<AnswerEvaluationResponse | null>(null);
  const [report, setReport] = useState<FinalReportResponse | null>(null);

  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Load available roles and sample resumes on mount
  useEffect(() => {
    async function initMetadata() {
      try {
        const [rolesData, samplesData] = await Promise.all([
          api.getRoles(),
          api.getSampleResumes(),
        ]);
        setRoles(rolesData);
        setSampleResumes(samplesData);
      } catch (err: any) {
        console.error('Initialization error:', err);
        setError('Could not connect to backend server. Make sure FastAPI is running on port 8000.');
      }
    }
    initMetadata();
  }, []);

  const handleReset = () => {
    setCurrentStep(1);
    setSession(null);
    setCurrentQuestion(null);
    setActiveFeedback(null);
    setReport(null);
    setError(null);
  };

  // Step 1: Upload file or pick sample
  const handleUploadFile = async (file: File, role: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const sess = await api.startSessionWithFile(file, role);
      setSession(sess);
      setCurrentStep(2);
    } catch (err: any) {
      setError(err.message || 'Failed to parse resume');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectSample = async (sampleId: string, role: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const sess = await api.startSessionWithSample(sampleId, role);
      setSession(sess);
      setCurrentStep(2);
    } catch (err: any) {
      setError(err.message || 'Failed to load sample resume');
    } finally {
      setIsLoading(false);
    }
  };

  // Step 2: Proceed from profile review to interview room
  const handleProceedToInterview = async () => {
    if (!session) return;
    setIsLoading(true);
    setError(null);
    try {
      const q = await api.getNextQuestion(session.session_id);
      setCurrentQuestion(q);
      setActiveFeedback(null);
      setCurrentStep(3);
    } catch (err: any) {
      setError(err.message || 'Failed to load initial question');
    } finally {
      setIsLoading(false);
    }
  };

  // Step 3: Submit answer
  const handleSubmitAnswer = async (answer: string): Promise<AnswerEvaluationResponse> => {
    if (!session) throw new Error('No active session');
    setIsSubmitting(true);
    setError(null);
    try {
      const feedback = await api.submitAnswer(session.session_id, answer);
      setActiveFeedback(feedback);
      return feedback;
    } catch (err: any) {
      setError(err.message || 'Failed to evaluate answer');
      throw err;
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleNextQuestion = async () => {
    if (!session) return;
    setIsLoading(true);
    setError(null);
    try {
      const nextQ = await api.getNextQuestion(session.session_id);
      setCurrentQuestion(nextQ);
      setActiveFeedback(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load next question');
    } finally {
      setIsLoading(false);
    }
  };

  const handleViewReport = async () => {
    if (!session) return;
    setIsLoading(true);
    setError(null);
    try {
      const rep = await api.getReport(session.session_id);
      setReport(rep);
      setCurrentStep(4);
    } catch (err: any) {
      setError(err.message || 'Failed to retrieve final report');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Header
        activeRole={session?.target_role}
        step={currentStep}
        onReset={handleReset}
      />

      <main className="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 py-6 sm:py-8 space-y-6">
        <Stepper currentStep={currentStep} />

        {currentStep === 1 && (
          <ResumeUploadStep
            roles={roles}
            sampleResumes={sampleResumes}
            onUploadFile={handleUploadFile}
            onSelectSample={handleSelectSample}
            isLoading={isLoading}
            error={error}
          />
        )}

        {currentStep === 2 && session && (
          <ProfileReviewStep
            session={session}
            onProceed={handleProceedToInterview}
            isLoading={isLoading}
          />
        )}

        {currentStep === 3 && currentQuestion && (
          <InterviewRoomStep
            question={currentQuestion}
            onSubmitAnswer={handleSubmitAnswer}
            onNextQuestion={handleNextQuestion}
            onViewReport={handleViewReport}
            isSubmitting={isSubmitting}
            activeFeedback={activeFeedback}
          />
        )}

        {currentStep === 4 && report && (
          <ReportStep
            report={report}
            onReset={handleReset}
          />
        )}
      </main>

      <footer className="border-t border-slate-900 py-6 text-center text-xs text-slate-500">
        <p>Enterprise AI Candidate Screening Engine &bull; Grounded in Standard ML &amp; Systems Literature &bull; FastAPI + ChromaDB + React</p>
      </footer>
    </div>
  );
}
export default App;
