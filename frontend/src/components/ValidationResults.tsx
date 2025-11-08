import { ValidationResult, IssueSeverity } from '@/lib/types';

interface Props {
  result: ValidationResult;
}

export default function ValidationResults({ result }: Props) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'passed':
        return {
          bg: 'bg-green-50',
          border: 'border-green-200',
          text: 'text-green-800',
        };
      case 'flagged':
        return {
          bg: 'bg-yellow-50',
          border: 'border-yellow-200',
          text: 'text-yellow-800',
        };
      case 'rejected':
        return {
          bg: 'bg-red-50',
          border: 'border-red-200',
          text: 'text-red-800',
        };
      default:
        return {
          bg: 'bg-gray-50',
          border: 'border-gray-200',
          text: 'text-gray-800',
        };
    }
  };

  const getSeverityColor = (severity: IssueSeverity) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-300';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'low':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getSeverityIcon = (severity: IssueSeverity) => {
    switch (severity) {
      case 'critical':
      case 'high':
        return '🔴';
      case 'medium':
        return '🟡';
      case 'low':
        return '🔵';
      default:
        return '⚪';
    }
  };

  const statusColors = getStatusColor(result.overall_status);

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-4">Validation Results</h2>

      {/* Summary Card */}
      <div className={`p-4 rounded-lg mb-6 ${statusColors.bg} border ${statusColors.border}`}>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <p className="text-sm text-gray-600 mb-1">Status</p>
            <p className={`text-2xl font-bold capitalize ${statusColors.text}`}>
              {result.overall_status}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600 mb-1">Risk Score</p>
            <p className="text-2xl font-bold">
              {result.risk_score.toFixed(1)}
              <span className="text-sm text-gray-500">/100</span>
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600 mb-1">Cost Impact</p>
            <p className="text-2xl font-bold text-red-600">
              ${result.total_cost_impact.toFixed(2)}
            </p>
          </div>
        </div>
        <div className="mt-3 pt-3 border-t border-gray-200">
          <p className="text-xs text-gray-500">
            Processed in {result.processing_time_ms}ms
          </p>
        </div>
      </div>

      {/* Issues List */}
      {result.issues.length > 0 ? (
        <div className="space-y-4">
          <h3 className="font-semibold text-lg">
            Issues Found ({result.issues.length})
          </h3>

          {result.issues.map((issue, idx) => (
            <div key={idx} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start gap-3">
                <div className="text-2xl mt-1">
                  {getSeverityIcon(issue.severity)}
                </div>
                <div className="flex-1">
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="font-semibold text-gray-900">
                      {issue.issue_type.split('_').map(word =>
                        word.charAt(0).toUpperCase() + word.slice(1)
                      ).join(' ')}
                    </h4>
                    <span className={`text-xs px-2 py-1 rounded border ${getSeverityColor(issue.severity)}`}>
                      {issue.severity.toUpperCase()}
                    </span>
                  </div>

                  <p className="text-sm text-gray-700 mb-2">
                    {issue.description}
                  </p>

                  <p className="text-sm text-gray-600 mb-3 italic">
                    {issue.explanation}
                  </p>

                  {issue.suggested_fix && (
                    <div className="mt-2 p-3 bg-blue-50 rounded border border-blue-200">
                      <p className="text-xs font-semibold text-blue-900 mb-1">
                        💡 Suggested Fix:
                      </p>
                      <p className="text-sm text-blue-800">{issue.suggested_fix}</p>
                    </div>
                  )}

                  <div className="flex gap-4 mt-3 text-xs text-gray-500">
                    <span>
                      ✓ Confidence: {(issue.confidence_score * 100).toFixed(0)}%
                    </span>
                    {issue.cost_impact !== null && (
                      <span className="text-red-600 font-medium">
                        💰 Impact: ${issue.cost_impact.toFixed(2)}
                      </span>
                    )}
                    <span className="text-gray-400">
                      • {issue.agent_name}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-8 bg-green-50 rounded-lg border border-green-200">
          <div className="text-4xl mb-2">✅</div>
          <p className="text-lg font-semibold text-green-800">No Issues Found</p>
          <p className="text-sm text-green-600 mt-1">
            This claim passed all validation checks
          </p>
        </div>
      )}
    </div>
  );
}
