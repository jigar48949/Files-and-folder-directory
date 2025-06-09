import React, { useState } from 'react';
import { X, Key, Save } from 'lucide-react';

interface AIConfigDialogProps {
  isOpen: boolean;
  onClose: () => void;
  config: {
    apiKey: string;
    model: string;
  };
  onSave: (config: { apiKey: string; model: string }) => void;
}

const AIConfigDialog: React.FC<AIConfigDialogProps> = ({
  isOpen,
  onClose,
  config,
  onSave
}) => {
  const [formData, setFormData] = useState(config);

  if (!isOpen) return null;

  const handleSave = () => {
    onSave(formData);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <Key className="h-6 w-6 text-blue-600" />
            <h2 className="text-xl font-semibold text-gray-900">AI Configuration</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Gemini API Key
            </label>
            <input
              type="password"
              value={formData.apiKey}
              onChange={(e) => setFormData({ ...formData, apiKey: e.target.value })}
              className="input"
              placeholder="Enter your Gemini API key"
            />
            <p className="text-xs text-gray-500 mt-1">
              Get your API key from{' '}
              <a
                href="https://makersuite.google.com/app/apikey"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800"
              >
                Google AI Studio
              </a>
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Model
            </label>
            <select
              value={formData.model}
              onChange={(e) => setFormData({ ...formData, model: e.target.value })}
              className="input"
            >
              <option value="gemini-pro">Gemini Pro</option>
              <option value="gemini-pro-vision">Gemini Pro Vision</option>
            </select>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="text-sm font-medium text-blue-900 mb-2">AI Features</h3>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Structure suggestions based on file types</li>
              <li>• Code summarization and analysis</li>
              <li>• Improvement recommendations</li>
              <li>• Smart file organization</li>
            </ul>
          </div>
        </div>

        <div className="flex justify-end gap-3 p-6 border-t border-gray-200">
          <button
            onClick={onClose}
            className="btn-secondary"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="btn-primary flex items-center gap-2"
          >
            <Save className="h-4 w-4" />
            Save Configuration
          </button>
        </div>
      </div>
    </div>
  );
};

export default AIConfigDialog;