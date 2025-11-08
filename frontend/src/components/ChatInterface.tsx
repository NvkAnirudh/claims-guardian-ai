'use client';

import { useState } from 'react';
import { askQuestion } from '@/lib/api';
import { ValidationResult } from '@/lib/types';

interface Props {
  claimId: string;
  validationResult: ValidationResult;
}

interface Message {
  question: string;
  answer: string;
}

export default function ChatInterface({ claimId, validationResult }: Props) {
  const [question, setQuestion] = useState('');
  const [conversation, setConversation] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAsk = async () => {
    if (!question.trim()) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await askQuestion(claimId, question);
      setConversation([...conversation, { question, answer: response.answer }]);
      setQuestion('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get answer');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleAsk();
    }
  };

  const suggestedQuestions = [
    "Why was this claim flagged?",
    "How can I fix these issues?",
    "What is the total financial impact?",
    "Is this claim likely to be denied?",
    "Which validator found the most issues?",
  ];

  return (
    <div className="bg-white rounded-lg shadow p-4 h-full flex flex-col">
      <h3 className="text-lg font-semibold mb-3">💬 Ask Questions About This Claim</h3>

      {/* Conversation History - Scrollable */}
      <div className="flex-1 overflow-y-auto mb-3 min-h-0">
        {conversation.length > 0 ? (
          <div className="space-y-3">
            {conversation.map((msg, idx) => (
              <div key={idx} className="space-y-2">
                {/* Question */}
                <div className="flex justify-end">
                  <div className="bg-blue-500 text-white p-2 rounded-lg max-w-[80%]">
                    <p className="text-sm">{msg.question}</p>
                  </div>
                </div>
                {/* Answer */}
                <div className="flex justify-start">
                  <div className="bg-gray-100 p-2 rounded-lg max-w-[80%]">
                    <p className="text-sm text-gray-700">{msg.answer}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="h-full flex flex-col justify-center">
            <p className="text-xs text-gray-600 mb-2">Suggested questions:</p>
            <div className="flex flex-wrap gap-2">
              {suggestedQuestions.map((q, idx) => (
                <button
                  key={idx}
                  onClick={() => setQuestion(q)}
                  className="text-xs px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-full transition-colors"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-2 p-2 bg-red-50 border border-red-200 rounded-md">
          <p className="text-xs text-red-800">{error}</p>
        </div>
      )}

      {/* Input - Fixed at bottom */}
      <div className="flex gap-2">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask a question..."
          className="flex-1 rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={isLoading}
        />
        <button
          onClick={handleAsk}
          disabled={isLoading || !question.trim()}
          className="bg-blue-600 text-white px-3 py-2 rounded-md hover:bg-blue-700 disabled:bg-gray-400 transition-colors flex items-center justify-center"
        >
          {isLoading ? (
            <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
          ) : (
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          )}
        </button>
      </div>
    </div>
  );
}
