import React from 'react';
import { X, Loader2 } from 'lucide-react';

interface ProgressDialogProps {
  isOpen: boolean;
  title: string;
  message: string;
  progress: number;
  onCancel?: () => void;
  canCancel?: boolean;
}

const ProgressDialog: React.FC<ProgressDialogProps> = ({
  isOpen,
  title,
  message,
  progress,
  onCancel,
  canCancel = true
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <Loader2 className="h-5 w-5 text-blue-600 animate-spin" />
            <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
          </div>
          {canCancel && onCancel && (
            <button
              onClick={onCancel}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="h-5 w-5" />
            </button>
          )}
        </div>

        <div className="p-6 space-y-4">
          <p className="text-sm text-gray-600">{message}</p>
          
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Progress</span>
              <span className="text-gray-900 font-medium">{Math.round(progress)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        </div>

        {canCancel && onCancel && (
          <div className="flex justify-end p-6 border-t border-gray-200">
            <button
              onClick={onCancel}
              className="btn-secondary"
            >
              Cancel
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProgressDialog;