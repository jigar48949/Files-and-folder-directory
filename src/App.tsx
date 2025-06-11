import React, { useState, useEffect } from 'react';
import { Folder, FileText, Settings, Package, History, Moon, Sun, Sparkles, Zap, Code } from 'lucide-react';
import StructureTab from './components/StructureTab';
import MoveFilesTab from './components/MoveFilesTab';
import OrganizeTab from './components/OrganizeTab';
import TemplatesTab from './components/TemplatesTab';
import EnhancedStructureTab from './components/enhanced/EnhancedStructureTab';
import SmartOrganizeTab from './components/enhanced/SmartOrganizeTab';
import FileExplorerTab from './components/FileExplorerTab';
import HistoryDialog from './components/HistoryDialog';
import AIConfigDialog from './components/AIConfigDialog';
import { DirectoryProvider } from './context/DirectoryContext.tsx';
import { useFileOperations } from './hooks/useFileOperations';
import { useAI } from './hooks/useAI';

const tabs = [
  { id: 'file-explorer', label: 'File Explorer & Editor', icon: Code },
  { id: 'enhanced-structure', label: 'Enhanced Structure (AI)', icon: Sparkles },
  { id: 'structure', label: 'Define & Create Structure', icon: Folder },
  { id: 'move', label: 'Quick Move Files', icon: FileText },
  { id: 'organize', label: 'Smart Organize & Package', icon: Package },
  { id: 'smart-organize', label: 'Advanced Smart Organize', icon: Zap },
  { id: 'templates', label: 'Manage Templates', icon: Settings },
];

function AppContent() {
  const [activeTab, setActiveTab] = useState('file-explorer');
  const [darkMode, setDarkMode] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [showAIConfig, setShowAIConfig] = useState(false);
  const { operations, undoLastOperation } = useFileOperations();
  const { config: aiConfig, updateConfig: updateAIConfig, loadConfig } = useAI();

  useEffect(() => {
    loadConfig();
  }, [loadConfig]);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    document.documentElement.classList.toggle('dark');
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'file-explorer':
        return <FileExplorerTab />;
      case 'structure':
        return <StructureTab />;
      case 'enhanced-structure':
        return <EnhancedStructureTab />;
      case 'move':
        return <MoveFilesTab />;
      case 'organize':
        return <OrganizeTab />;
      case 'smart-organize':
        return <SmartOrganizeTab />;
      case 'templates':
        return <TemplatesTab />;
      default:
        return <FileExplorerTab />;
    }
  };

  return (
    <div className={`min-h-screen bg-gray-50 ${darkMode ? 'dark' : ''}`}>
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-3">
              <Folder className="h-8 w-8 text-blue-600" />
              <h1 className="text-2xl font-bold text-gray-900">Directory Tool Pro</h1>
              <span className="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded">v2.0</span>
              <span className="text-xs text-purple-600 bg-purple-100 px-2 py-1 rounded font-medium">
                AI Enhanced
              </span>
            </div>
            
            <div className="flex items-center gap-4">
              <button
                onClick={() => setShowAIConfig(true)}
                className="p-2 rounded-md hover:bg-gray-100 transition-colors"
                title="AI Configuration"
              >
                <Sparkles className="h-5 w-5 text-purple-600" />
              </button>
              
              <button
                onClick={toggleDarkMode}
                className="p-2 rounded-md hover:bg-gray-100 transition-colors"
                title="Toggle theme"
              >
                {darkMode ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
              </button>
              
              <button 
                onClick={() => setShowHistory(true)}
                className="p-2 rounded-md hover:bg-gray-100 transition-colors relative" 
                title="View history"
              >
                <History className="h-5 w-5" />
                {operations.length > 0 && (
                  <span className="absolute -top-1 -right-1 bg-blue-600 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                    {operations.length > 9 ? '9+' : operations.length}
                  </span>
                )}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-1 overflow-x-auto">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-4 py-3 text-sm font-medium rounded-t-lg transition-colors whitespace-nowrap ${
                    activeTab === tab.id
                      ? 'tab-active border-b-2 border-blue-600'
                      : 'tab-inactive'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {renderTabContent()}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center text-sm text-gray-500">
            <p>© 2025 Directory Tool Pro - AI-Enhanced Directory Management with Code Editor</p>
            <div className="flex items-center gap-4">
              <span>Operations: {operations.length}</span>
              <span className={`px-2 py-1 rounded text-xs ${
                aiConfig.apiKey ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
              }`}>
                AI: {aiConfig.apiKey ? 'Configured' : 'Not Configured'}
              </span>
            </div>
          </div>
        </div>
      </footer>

      {/* Dialogs */}
      <HistoryDialog
        isOpen={showHistory}
        onClose={() => setShowHistory(false)}
        operations={operations}
        onUndo={undoLastOperation}
      />

      <AIConfigDialog
        isOpen={showAIConfig}
        onClose={() => setShowAIConfig(false)}
        config={aiConfig}
        onSave={updateAIConfig}
      />
    </div>
  );
}

function App() {
  return (
    <DirectoryProvider>
      <AppContent />
    </DirectoryProvider>
  );
}

export default App;