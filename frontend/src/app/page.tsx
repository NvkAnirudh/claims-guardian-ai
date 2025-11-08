'use client';

import { useState } from 'react';
import ClaimInput from '@/components/ClaimInput';
import ValidationResults from '@/components/ValidationResults';
import ChatInterface from '@/components/ChatInterface';
import { Claim, ValidationResult } from '@/lib/types';
import { validateClaim } from '@/lib/api';

export default function Home() {
  const [claim, setClaim] = useState<Claim | null>(null);
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleValidate = async (claimData: Claim) => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await validateClaim(claimData);
      setClaim(claimData);
      setValidationResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Validation failed');
      setValidationResult(null);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900">
            Claims Guardian AI
          </h1>
          <p className="text-gray-600 mt-1">
            AI-Powered Medical Claims Validation with Multi-Agent System
          </p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left: Claim Input */}
          <div>
            <ClaimInput onSubmit={handleValidate} isLoading={isLoading} />
          </div>

          {/* Right: Results and Chat */}
          <div className="flex flex-col h-[calc(100vh-12rem)] sticky top-4">
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
                <h3 className="text-lg font-semibold text-red-800 mb-2">Error</h3>
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}

            {validationResult && claim ? (
              <>
                {/* Scrollable Results Section */}
                <div className="flex-1 overflow-y-auto mb-4 min-h-0">
                  <ValidationResults result={validationResult} />
                </div>

                {/* Fixed Chat Section */}
                <div className="flex-shrink-0 h-80">
                  <ChatInterface
                    claimId={claim.claim_id}
                    validationResult={validationResult}
                  />
                </div>
              </>
            ) : (
              !error && (
                <div className="bg-white rounded-lg shadow p-8 text-center">
                  <div className="text-6xl mb-4">🏥</div>
                  <h2 className="text-xl font-semibold text-gray-900 mb-2">
                    Ready to Validate
                  </h2>
                  <p className="text-gray-600 mb-4">
                    Enter claim details or load a sample to get started
                  </p>
                  <div className="text-left bg-blue-50 rounded-lg p-4 border border-blue-200">
                    <h3 className="font-semibold text-blue-900 mb-2">
                      🤖 Multi-Agent Validation System
                    </h3>
                    <ul className="text-sm text-blue-800 space-y-1">
                      <li>• CPT-ICD-10 Compatibility Validator</li>
                      <li>• Bundling/Unbundling Detector</li>
                      <li>• Modifier Compliance Checker</li>
                      <li>• Demographic Rule Validator</li>
                      <li>• Cost Anomaly Analyzer</li>
                    </ul>
                  </div>
                </div>
              )
            )}
          </div>
        </div>
      </main>

      <footer className="bg-white border-t mt-12">
        <div className="max-w-7xl mx-auto px-4 py-6 text-center text-sm text-gray-500">
          <p>
            Claims Guardian AI - Open Source Medical Claims Validation System
          </p>
        </div>
      </footer>
    </div>
  );
}
