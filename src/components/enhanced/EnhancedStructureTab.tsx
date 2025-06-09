import React, { useState, useRef } from 'react';
import { Play, Eye, Trash2, Save, FolderPlus, FileText, Sparkles, Download, Upload } from 'lucide-react';
import { useDirectory } from '../../context/DirectoryContext';
import { useFileOperations } from '../../hooks/useFileOperations';
import { useAI } from '../../hooks/useAI';
import ProgressDialog from '../ProgressDialog';
import AIConfigDialog from '../AIConfigDialog';

const EnhancedStructureTab: React.FC = () => {
  const { currentStructure, setCurrentStructure, addOperation } = useDirectory();
  const { createStructure, parseStructureDefinition } = useFileOperations();
  const { config: aiConfig, updateConfig: updateAIConfig, suggestStructure, isLoading: aiLoading } = useAI();
  
  const [previewMode, setPreviewMode] = useState(false);
  const [createdItems, setCreatedItems] = useState<string[]>([]);
  const [baseDirectory, setBaseDirectory] = useState('/project');
  const [showProgress, setShowProgress] = useState(false);
  const [progress, setProgress] = useState(0);
  const [progressMessage, setProgressMessage] = useState('');
  const [showAIConfig, setShowAIConfig] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const sampleStructures = {
    'React Project': `project/
  src/
    components/
      Header.tsx
      Footer.tsx
      Layout.tsx
    pages/
      Home.tsx
      About.tsx
      Contact.tsx
    hooks/
      useAuth.ts
      useApi.ts
    utils/
      helpers.ts
      constants.ts
    styles/
      globals.css
      components.css
    types/
      index.ts
  public/
    images/
    icons/
    favicon.ico
  tests/
    components/
    pages/
    utils/
  docs/
    README.md
    CONTRIBUTING.md
  package.json
  tsconfig.json
  .gitignore`,
    
    'Python Package': `my_package/
  src/
    my_package/
      __init__.py
      core.py
      utils.py
      models/
        __init__.py
        base.py
        user.py
      api/
        __init__.py
        endpoints.py
        middleware.py
    tests/
      __init__.py
      test_core.py
      test_utils.py
      test_models.py
  docs/
    index.md
    api.md
    examples/
      basic_usage.py
      advanced_usage.py
  scripts/
    setup.py
    deploy.py
  requirements.txt
  setup.py
  README.md
  .gitignore`,
    
    'Full-Stack App': `fullstack_app/
  frontend/
    src/
      components/
        ui/
        forms/
        layout/
      pages/
      hooks/
      services/
      styles/
    public/
    package.json
  backend/
    src/
      controllers/
      models/
      middleware/
      routes/
      utils/
      config/
    tests/
    package.json
  database/
    migrations/
    seeds/
    schema.sql
  docs/
    api.md
    deployment.md
  docker-compose.yml
  README.md`
  };

  const handleCreateStructure = async () => {
    if (!currentStructure.trim()) {
      alert('Please enter a directory structure');
      return;
    }

    if (!baseDirectory.trim()) {
      alert('Please specify a base directory');
      return;
    }

    setShowProgress(true);
    setProgress(0);
    setProgressMessage('Starting structure creation...');

    try {
      const result = await createStructure(
        currentStructure,
        baseDirectory,
        (progress, message) => {
          setProgress(progress);
          setProgressMessage(message);
        }
      );

      if (result.success) {
        const items = parseStructureDefinition(currentStructure);
        const created = items.map(item => 
          `${item.type === 'directory' ? '📁' : '📄'} ${item.path}`
        );
        setCreatedItems(created);
        alert(`Successfully created structure with ${result.processedCount} items!`);
      }
    } catch (error) {
      alert('Failed to create structure');
    } finally {
      setShowProgress(false);
    }
  };

  const handleAISuggestion = async () => {
    if (!aiConfig.apiKey) {
      setShowAIConfig(true);
      return;
    }

    try {
      // Get file extensions from current structure or use common ones
      const extensions = ['.js', '.ts', '.tsx', '.css', '.html', '.py', '.md'];
      const suggestion = await suggestStructure(extensions);
      setCurrentStructure(suggestion);
      addOperation({
        operation: 'ai_suggest_structure',
        details: 'AI suggested structure loaded',
        status: 'success'
      });
    } catch (error) {
      alert('Failed to get AI suggestion. Please check your API configuration.');
    }
  };

  const loadSample = (sampleName: string) => {
    setCurrentStructure(sampleStructures[sampleName as keyof typeof sampleStructures]);
  };

  const exportStructure = () => {
    if (!currentStructure.trim()) {
      alert('No structure to export');
      return;
    }

    const blob = new Blob([currentStructure], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'directory_structure.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const importStructure = () => {
    fileInputRef.current?.click();
  };

  const handleFileImport = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target?.result as string;
        setCurrentStructure(content);
      };
      reader.readAsText(file);
    }
  };

  const getLineNumbers = () => {
    const lines = currentStructure.split('\n').length;
    return Array.from({ length: lines }, (_, i) => i + 1).join('\n');
  };

  const renderPreview = () => {
    if (!previewMode || !currentStructure.trim()) return null;
    
    const items = parseStructureDefinition(currentStructure);
    
    return (
      <div className="mt-4 p-4 bg-gray-50 rounded-lg border">
        <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
          <Eye className="h-5 w-5" />
          Structure Preview
        </h3>
        <div className="space-y-1 font-mono text-sm max-h-64 overflow-y-auto">
          {items.map((item, index) => (
            <div
              key={index}
              className="flex items-center gap-2"
              style={{ paddingLeft: `${item.depth * 20}px` }}
            >
              {item.type === 'directory' ? (
                <FolderPlus className="h-4 w-4 text-blue-600" />
              ) : (
                <FileText className="h-4 w-4 text-gray-600" />
              )}
              <span className={item.type === 'directory' ? 'font-semibold text-blue-700' : 'text-gray-700'}>
                {item.name}
              </span>
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Enhanced Structure Creation</h2>
          <p className="text-gray-600 mt-1">
            Define directory structures with AI assistance and advanced features
          </p>
        </div>
        
        <div className="flex gap-2">
          <select
            onChange={(e) => e.target.value && loadSample(e.target.value)}
            className="input w-48"
            defaultValue=""
          >
            <option value="">Load Sample Structure</option>
            {Object.keys(sampleStructures).map(name => (
              <option key={name} value={name}>{name}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Base Directory */}
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
              className="input"
              placeholder="/path/to/create/structure"
            />
          </div>
        </div>
      </div>

      {/* Structure Definition */}
      <div className="card p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">Structure Definition</h3>
          <div className="flex gap-2">
            <button
              onClick={importStructure}
              className="btn-outline text-sm flex items-center gap-2"
            >
              <Upload className="h-4 w-4" />
              Import
            </button>
            <button
              onClick={exportStructure}
              className="btn-outline text-sm flex items-center gap-2"
            >
              <Download className="h-4 w-4" />
              Export
            </button>
            <button
              onClick={handleAISuggestion}
              className="btn-outline text-sm flex items-center gap-2"
              disabled={aiLoading}
            >
              <Sparkles className="h-4 w-4" />
              {aiLoading ? 'Generating...' : 'AI Suggest'}
            </button>
          </div>
        </div>
        
        <div className="flex border border-gray-300 rounded-lg overflow-hidden">
          <div className="line-numbers">
            {getLineNumbers()}
          </div>
          <textarea
            value={currentStructure}
            onChange={(e) => setCurrentStructure(e.target.value)}
            className="code-editor flex-1 border-0 focus:ring-0 focus:outline-none p-3"
            rows={15}
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
        </div>
        
        <div className="flex justify-between items-center mt-4">
          <div className="flex gap-2">
            <button 
              onClick={handleCreateStructure} 
              className="btn-primary flex items-center gap-2"
              disabled={!currentStructure.trim() || !baseDirectory.trim()}
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
              onClick={() => setCurrentStructure('')}
              className="btn-secondary flex items-center gap-2"
            >
              <Trash2 className="h-4 w-4" />
              Clear
            </button>
          </div>
          
          <div className="text-sm text-gray-500">
            Lines: {currentStructure.split('\n').length} | 
            Characters: {currentStructure.length}
          </div>
        </div>
      </div>

      {/* Preview */}
      {renderPreview()}

      {/* Created Items */}
      {createdItems.length > 0 && (
        <div className="card p-6">
          <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
            <Save className="h-5 w-5 text-green-600" />
            Recently Created Items
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2 max-h-60 overflow-y-auto">
            {createdItems.map((item, index) => (
              <div key={index} className="text-sm font-mono bg-gray-50 p-2 rounded">
                {item}
              </div>
            ))}
          </div>
          <button
            onClick={() => setCreatedItems([])}
            className="btn-secondary mt-3 text-sm"
          >
            Clear List
          </button>
        </div>
      )}

      {/* Help */}
      <div className="card p-6 bg-blue-50 border-blue-200">
        <h3 className="text-lg font-semibold text-blue-900 mb-2">Enhanced Features</h3>
        <div className="text-sm text-blue-800 space-y-2">
          <p><strong>AI Suggestions:</strong> Get intelligent structure recommendations</p>
          <p><strong>Import/Export:</strong> Save and share structure definitions</p>
          <p><strong>Live Preview:</strong> Visualize your structure before creation</p>
          <p><strong>Sample Templates:</strong> Start with proven project structures</p>
          <p><strong>Progress Tracking:</strong> Monitor creation progress in real-time</p>
        </div>
      </div>

      {/* Hidden file input for import */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".txt,.md"
        onChange={handleFileImport}
        className="hidden"
      />

      {/* Progress Dialog */}
      <ProgressDialog
        isOpen={showProgress}
        title="Creating Structure"
        message={progressMessage}
        progress={progress}
        onCancel={() => setShowProgress(false)}
      />

      {/* AI Config Dialog */}
      <AIConfigDialog
        isOpen={showAIConfig}
        onClose={() => setShowAIConfig(false)}
        config={aiConfig}
        onSave={updateAIConfig}
      />
    </div>
  );
};

export default EnhancedStructureTab;