import React, { useState } from 'react';
import { Save, Download, Upload, Trash2, Plus } from 'lucide-react';

interface Template {
  id: string;
  name: string;
  description: string;
  structure: string;
  created: string;
}

const TemplatesTab: React.FC = () => {
  const [templates, setTemplates] = useState<Template[]>([
    {
      id: '1',
      name: 'React Project',
      description: 'Standard React application structure',
      structure: `project/
  src/
    components/
    pages/
    hooks/
    utils/
  public/
  package.json`,
      created: '2025-01-01'
    },
    {
      id: '2',
      name: 'Node.js API',
      description: 'Express.js API server structure',
      structure: `api/
  src/
    controllers/
    models/
    routes/
    middleware/
  tests/
  package.json`,
      created: '2025-01-01'
    }
  ]);

  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newTemplate, setNewTemplate] = useState({
    name: '',
    description: '',
    structure: ''
  });

  const handleCreateTemplate = () => {
    if (!newTemplate.name.trim() || !newTemplate.structure.trim()) {
      alert('Please fill in name and structure');
      return;
    }

    const template: Template = {
      id: Date.now().toString(),
      name: newTemplate.name,
      description: newTemplate.description,
      structure: newTemplate.structure,
      created: new Date().toISOString().split('T')[0]
    };

    setTemplates([...templates, template]);
    setNewTemplate({ name: '', description: '', structure: '' });
    setShowCreateForm(false);
    alert('Template created successfully!');
  };

  const handleDeleteTemplate = (id: string) => {
    if (confirm('Are you sure you want to delete this template?')) {
      setTemplates(templates.filter(t => t.id !== id));
      if (selectedTemplate?.id === id) {
        setSelectedTemplate(null);
      }
    }
  };

  const handleLoadTemplate = (template: Template) => {
    alert(`Loading template "${template.name}" to structure definition`);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Manage Templates</h2>
          <p className="text-gray-600 mt-1">
            Save, load, and manage directory structure templates
          </p>
        </div>
        <button
          onClick={() => setShowCreateForm(true)}
          className="btn-primary flex items-center gap-2"
        >
          <Plus className="h-4 w-4" />
          New Template
        </button>
      </div>

      {showCreateForm && (
        <div className="card p-6">
          <h3 className="text-lg font-semibold mb-4">Create New Template</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Template Name
              </label>
              <input
                type="text"
                value={newTemplate.name}
                onChange={(e) => setNewTemplate({ ...newTemplate, name: e.target.value })}
                className="input w-full"
                placeholder="Enter template name"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description
              </label>
              <input
                type="text"
                value={newTemplate.description}
                onChange={(e) => setNewTemplate({ ...newTemplate, description: e.target.value })}
                className="input w-full"
                placeholder="Enter template description"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Structure Definition
              </label>
              <textarea
                value={newTemplate.structure}
                onChange={(e) => setNewTemplate({ ...newTemplate, structure: e.target.value })}
                className="textarea w-full h-32"
                placeholder="Enter directory structure..."
              />
            </div>
            <div className="flex gap-3">
              <button
                onClick={handleCreateTemplate}
                className="btn-primary flex items-center gap-2"
              >
                <Save className="h-4 w-4" />
                Save Template
              </button>
              <button
                onClick={() => setShowCreateForm(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card p-6">
          <h3 className="text-lg font-semibold mb-4">Available Templates</h3>
          <div className="space-y-2">
            {templates.map((template) => (
              <div
                key={template.id}
                className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                  selectedTemplate?.id === template.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:bg-gray-50'
                }`}
                onClick={() => setSelectedTemplate(template)}
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900">{template.name}</h4>
                    <p className="text-sm text-gray-600 mt-1">{template.description}</p>
                    <p className="text-xs text-gray-500 mt-2">Created: {template.created}</p>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteTemplate(template.id);
                    }}
                    className="text-red-600 hover:text-red-800 p-1"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="card p-6">
          <h3 className="text-lg font-semibold mb-4">Template Preview</h3>
          {selectedTemplate ? (
            <div className="space-y-4">
              <div>
                <h4 className="font-medium text-gray-900">{selectedTemplate.name}</h4>
                <p className="text-sm text-gray-600">{selectedTemplate.description}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Structure
                </label>
                <pre className="bg-gray-50 p-4 rounded-lg text-sm font-mono overflow-auto max-h-64">
                  {selectedTemplate.structure}
                </pre>
              </div>
              <div className="flex gap-3">
                <button
                  onClick={() => handleLoadTemplate(selectedTemplate)}
                  className="btn-primary flex items-center gap-2"
                >
                  <Upload className="h-4 w-4" />
                  Load to Editor
                </button>
                <button className="btn-outline flex items-center gap-2">
                  <Download className="h-4 w-4" />
                  Export
                </button>
              </div>
            </div>
          ) : (
            <div className="text-center text-gray-500 py-8">
              <Save className="h-12 w-12 mx-auto mb-2 opacity-50" />
              <p>Select a template to preview</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TemplatesTab;