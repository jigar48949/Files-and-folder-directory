import React from 'react';
import { X, Clock, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { Operation } from '../hooks/useFileOperations';

interface HistoryDialogProps {
  isOpen: boolean;
  onClose: () => void;
  operations: Operation[];
  onUndo?: () => void;
}

const HistoryDialog: React.FC<HistoryDialogProps> = ({
  isOpen,
  onClose,
  operations,
  onUndo
}) => {
  if (!isOpen) return null;

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'error':
        return <XCircle className="h-4 w-4 text-red-600" />;
      case 'pending':
        return <AlertCircle className="h-4 w-4 text-yellow-600" />;
      default:
        return <Clock className="h-4 w-4 text-gray-600" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'text-green-600 bg-green-50';
      case 'error':
        return 'text-red-600 bg-red-50';
      case 'pending':
        return 'text-yellow-600 bg-yellow-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  const canUndo = operations.some(op => op.status === 'success');

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl mx-4 max-h-[80vh] flex flex-col">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <Clock className="h-6 w-6 text-blue-600" />
            <h2 className="text-xl font-semibold text-gray-900">Operation History</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6">
          {operations.length === 0 ? (
            <div className="text-center py-8">
              <Clock className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No operations recorded yet</p>
            </div>
          ) : (
            <div className="space-y-4">
              {operations.map((operation) => (
                <div
                  key={operation.id}
                  className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3 flex-1">
                      {getStatusIcon(operation.status)}
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-medium text-gray-900">
                            {operation.type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                          </h3>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(operation.status)}`}>
                            {operation.status}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">{operation.details}</p>
                        <p className="text-xs text-gray-500">
                          {formatTimestamp(operation.timestamp)}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="flex justify-between items-center p-6 border-t border-gray-200">
          <div className="text-sm text-gray-600">
            {operations.length} operation{operations.length !== 1 ? 's' : ''} recorded
          </div>
          <div className="flex gap-3">
            {canUndo && onUndo && (
              <button
                onClick={() => {
                  onUndo();
                  onClose();
                }}
                className="btn-outline"
              >
                Undo Last
              </button>
            )}
            <button
              onClick={onClose}
              className="btn-primary"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HistoryDialog;