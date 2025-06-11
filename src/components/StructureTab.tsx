import React, { useState } from 'react';
import { Play, Eye, Trash2, Save, FolderPlus, FileText } from 'lucide-react';

const StructureTab: React.FC = () => {
  const [structure, setStructure] = useState('');
  const [baseDirectory, setBaseDirectory] = useState('/project');
  const [previewMode, setPreviewMode] = useState(false);

  const handleCreateStructure = () => {
    if (!structure.trim()) {
      alert('Please enter a directory structure');
      return;
    }
    alert('Structure creation simulated successfully!');
  };

  const loadSample = () => {
    const sample = `project/
  src/
    components/
      Header.tsx
      Footer.tsx
    pages/
      Home.tsx
      About.tsx
    utils/
      helpers.ts
    styles/
      globals.css
  public/
    images/
  package.json
  README.md`;
    setStructure(sample);
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Define & Create Structure</h2>
        <p className="text-gray-600 mt-1">
          Define directory structures using indented text format
        </p>
      </div>

      <div className="card p-6">
        <h3 className="text-lg font-semibold mb-4">Base Directory</h3>
        <div className="flex gap-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Target Directory Path
            </label>
            <input
              type="text"
              value={baseDirectory}
              onChange={(e) => setBaseDirectory(e.target.value)}
              className="input w-full"
              placeholder="/path/to/create/structure"
            />
          </div>
        </div>
      </div>

      <div className="card p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">Structure Definition</h3>
          <button
            onClick={loadSample}
            className="btn-outline text-sm"
          >
            Load Sample
          </button>
        </div>
        
        <textarea
          value={structure}
          onChange={(e) => setStructure(e.target.value)}
          className="textarea w-full h-64 font-mono text-sm"
          placeholder={`Enter your directory structure here, for example:

project/
  src/
    components/
      Header.tsx
      Footer.tsx
    pages/
      Home.tsx
    styles/
      main.css
  public/
    images/
  package.json
  README.md`}
        />
        
        <div className="flex justify-between items-center mt-4">
          <div className="flex gap-2">
            <button 
              onClick={handleCreateStructure} 
              className="btn-primary flex items-center gap-2"
            >
              <Play className="h-4 w-4" />
              Create Structure
            </button>
            
            <button 
              onClick={() => setPreviewMode(!previewMode)} 
              className="btn-outline flex items-center gap-2"
            >
              <Eye className="h-4 w-4" />
              {previewMode ? 'Hide Preview' : 'Preview Structure'}
            </button>
            
            <button
              onClick={() => setStructure('')}
              className="btn-secondary flex items-center gap-2"
            >
              <Trash2 className="h-4 w-4" />
              Clear
            </button>
          </div>
          
          <div className="text-sm text-gray-500">
            Lines: {structure.split('\n').length} | 
            Characters: {structure.length}
          </div>
        </div>
      </div>

      {previewMode && structure && (
        <div className="card p-6">
          <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
            <Eye className="h-5 w-5" />
            Structure Preview
          </h3>
          <pre className="bg-gray-50 p-4 rounded-lg text-sm font-mono overflow-auto max-h-64">
            {structure}
          </pre>
        </div>
      )}
    </div>
  );
};

export default StructureTab;