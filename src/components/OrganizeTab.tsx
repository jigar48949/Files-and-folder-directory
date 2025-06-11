import React, { useState } from 'react';
import { Package, Archive, Target, Settings } from 'lucide-react';

const OrganizeTab: React.FC = () => {
  const [stagedFiles, setStagedFiles] = useState<string[]>([]);
  const [targetStructure, setTargetStructure] = useState('');

  const addToStage = () => {
    const newFile = `file_${stagedFiles.length + 1}.txt`;
    setStagedFiles([...stagedFiles, newFile]);
  };

  const clearStage = () => {
    setStagedFiles([]);
  };

  const organizeFiles = () => {
    if (stagedFiles.length === 0) {
      alert('No files staged for organization');
      return;
    }
    alert(`Organizing ${stagedFiles.length} files according to target structure`);
  };

  const createPackage = () => {
    if (stagedFiles.length === 0) {
      alert('No files to package');
      return;
    }
    alert(`Creating package with ${stagedFiles.length} files`);
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Smart Organize & Package</h2>
        <p className="text-gray-600 mt-1">
          Stage files and organize them according to a defined structure
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <Package className="h-5 w-5" />
              File Staging Area
            </h3>
            <div className="flex gap-2">
              <button
                onClick={addToStage}
                className="btn-outline text-sm"
              >
                Add File
              </button>
              <button
                onClick={clearStage}
                className="btn-secondary text-sm"
              >
                Clear
              </button>
            </div>
          </div>
          
          <div className="border border-gray-200 rounded-lg p-4 min-h-48">
            {stagedFiles.length === 0 ? (
              <div className="text-center text-gray-500 py-8">
                <Package className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p>No files staged</p>
                <p className="text-sm">Add files to get started</p>
              </div>
            ) : (
              <div className="space-y-2">
                {stagedFiles.map((file, index) => (
                  <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <span className="text-sm font-medium">{file}</span>
                    <span className="status-indicator bg-blue-100 text-blue-800">Staged</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="card p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Target className="h-5 w-5" />
            Target Structure
          </h3>
          
          <textarea
            value={targetStructure}
            onChange={(e) => setTargetStructure(e.target.value)}
            className="textarea w-full h-48"
            placeholder={`Define your target structure:

organized/
  documents/
    reports/
    presentations/
  media/
    images/
    videos/`}
          />
        </div>
      </div>

      <div className="card p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Settings className="h-5 w-5" />
          Organization Settings
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Operation Mode
            </label>
            <select className="input w-full">
              <option>Copy Files</option>
              <option>Move Files</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Conflict Resolution
            </label>
            <select className="input w-full">
              <option>Rename Duplicates</option>
              <option>Overwrite</option>
              <option>Skip</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Base Directory
            </label>
            <input
              type="text"
              className="input w-full"
              placeholder="/output/directory"
            />
          </div>
        </div>
      </div>

      <div className="flex justify-between items-center">
        <div className="text-sm text-gray-600">
          {stagedFiles.length} file(s) staged for organization
        </div>
        <div className="flex gap-3">
          <button
            onClick={organizeFiles}
            className="btn-primary flex items-center gap-2"
            disabled={stagedFiles.length === 0}
          >
            <Target className="h-4 w-4" />
            Organize Files
          </button>
          <button
            onClick={createPackage}
            className="btn-outline flex items-center gap-2"
            disabled={stagedFiles.length === 0}
          >
            <Archive className="h-4 w-4" />
            Create Package
          </button>
        </div>
      </div>
    </div>
  );
};

export default OrganizeTab;