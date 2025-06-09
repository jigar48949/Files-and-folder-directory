import React, { useState, useEffect } from 'react';
import { 
  Folder, 
  File, 
  FolderOpen, 
  Edit3, 
  Save, 
  X, 
  Plus, 
  Trash2, 
  Search,
  ChevronRight,
  ChevronDown,
  Code,
  FileText,
  Image,
  Archive
} from 'lucide-react';

interface FileNode {
  id: string;
  name: string;
  type: 'file' | 'directory';
  path: string;
  size?: number;
  modified?: string;
  content?: string;
  children?: FileNode[];
  isExpanded?: boolean;
}

const FileExplorerTab: React.FC = () => {
  const [fileTree, setFileTree] = useState<FileNode[]>([]);
  const [selectedFile, setSelectedFile] = useState<FileNode | null>(null);
  const [editingFile, setEditingFile] = useState<FileNode | null>(null);
  const [fileContent, setFileContent] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  // Initialize with sample file structure
  useEffect(() => {
    const sampleFiles: FileNode[] = [
      {
        id: '1',
        name: 'src',
        type: 'directory',
        path: '/src',
        isExpanded: true,
        children: [
          {
            id: '2',
            name: 'components',
            type: 'directory',
            path: '/src/components',
            isExpanded: true,
            children: [
              {
                id: '3',
                name: 'App.tsx',
                type: 'file',
                path: '/src/components/App.tsx',
                size: 2048,
                modified: '2025-01-01T10:00:00Z',
                content: `import React from 'react';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Welcome to React</h1>
        <p>
          Edit <code>src/App.tsx</code> and save to reload.
        </p>
      </header>
    </div>
  );
}

export default App;`
              },
              {
                id: '4',
                name: 'Header.tsx',
                type: 'file',
                path: '/src/components/Header.tsx',
                size: 1024,
                modified: '2025-01-01T09:30:00Z',
                content: `import React from 'react';

interface HeaderProps {
  title: string;
  subtitle?: string;
}

const Header: React.FC<HeaderProps> = ({ title, subtitle }) => {
  return (
    <header className="header">
      <h1>{title}</h1>
      {subtitle && <p className="subtitle">{subtitle}</p>}
    </header>
  );
};

export default Header;`
              }
            ]
          },
          {
            id: '5',
            name: 'styles',
            type: 'directory',
            path: '/src/styles',
            children: [
              {
                id: '6',
                name: 'App.css',
                type: 'file',
                path: '/src/styles/App.css',
                size: 512,
                modified: '2025-01-01T08:00:00Z',
                content: `.App {
  text-align: center;
}

.App-header {
  background-color: #282c34;
  padding: 20px;
  color: white;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.header {
  padding: 1rem;
  border-bottom: 1px solid #eee;
}

.subtitle {
  color: #666;
  margin-top: 0.5rem;
}`
              }
            ]
          },
          {
            id: '7',
            name: 'utils',
            type: 'directory',
            path: '/src/utils',
            children: [
              {
                id: '8',
                name: 'helpers.ts',
                type: 'file',
                path: '/src/utils/helpers.ts',
                size: 768,
                modified: '2025-01-01T11:00:00Z',
                content: `// Utility functions for the application

export const formatDate = (date: Date): string => {
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};

export const formatFileSize = (bytes: number): string => {
  const units = ['B', 'KB', 'MB', 'GB'];
  let size = bytes;
  let unitIndex = 0;
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }
  
  return \`\${size.toFixed(1)} \${units[unitIndex]}\`;
};

export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  delay: number
): ((...args: Parameters<T>) => void) => {
  let timeoutId: NodeJS.Timeout;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
};`
              }
            ]
          }
        ]
      },
      {
        id: '9',
        name: 'public',
        type: 'directory',
        path: '/public',
        children: [
          {
            id: '10',
            name: 'index.html',
            type: 'file',
            path: '/public/index.html',
            size: 1536,
            modified: '2025-01-01T07:00:00Z',
            content: `<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta
      name="description"
      content="Web site created using create-react-app"
    />
    <title>React App</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>`
          }
        ]
      },
      {
        id: '11',
        name: 'package.json',
        type: 'file',
        path: '/package.json',
        size: 1024,
        modified: '2025-01-01T06:00:00Z',
        content: `{
  "name": "directory-tool-web",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "lucide-react": "^0.263.1",
    "clsx": "^2.0.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}`
      },
      {
        id: '12',
        name: 'README.md',
        type: 'file',
        path: '/README.md',
        size: 2048,
        modified: '2025-01-01T05:00:00Z',
        content: `# Directory Tool Web

A modern web-based directory management and file organization tool.

## Features

- 📁 Directory structure creation and management
- 🤖 AI-powered structure suggestions
- 📦 Smart file organization and packaging
- 🔍 File explorer with code editing
- 📝 Template management
- 🎨 Modern, responsive UI

## Getting Started

1. Clone the repository
2. Install dependencies: \`npm install\`
3. Start the development server: \`npm start\`
4. Open [http://localhost:3000](http://localhost:3000) to view it in the browser

## Usage

### File Explorer
- Browse files and directories in the left panel
- Click on files to view their content
- Edit files directly in the code editor
- Save changes with Ctrl+S

### Directory Structure Creation
- Use the Enhanced Structure tab to create directory hierarchies
- Get AI suggestions based on your project type
- Import/export structure definitions

### Smart Organization
- Stage files for organization
- Define target structures
- Use AI to auto-assign files to appropriate locations
- Create organized packages

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details.`
      }
    ];

    setFileTree(sampleFiles);
  }, []);

  const getFileIcon = (file: FileNode) => {
    if (file.type === 'directory') {
      return file.isExpanded ? <FolderOpen className="h-4 w-4" /> : <Folder className="h-4 w-4" />;
    }

    const extension = file.name.split('.').pop()?.toLowerCase();
    switch (extension) {
      case 'tsx':
      case 'ts':
      case 'js':
      case 'jsx':
        return <Code className="h-4 w-4 text-blue-600" />;
      case 'css':
      case 'scss':
      case 'sass':
        return <FileText className="h-4 w-4 text-purple-600" />;
      case 'html':
        return <FileText className="h-4 w-4 text-orange-600" />;
      case 'md':
        return <FileText className="h-4 w-4 text-gray-600" />;
      case 'json':
        return <FileText className="h-4 w-4 text-yellow-600" />;
      case 'png':
      case 'jpg':
      case 'jpeg':
      case 'gif':
      case 'svg':
        return <Image className="h-4 w-4 text-green-600" />;
      case 'zip':
      case 'tar':
      case 'gz':
        return <Archive className="h-4 w-4 text-red-600" />;
      default:
        return <File className="h-4 w-4 text-gray-600" />;
    }
  };

  const toggleDirectory = (nodeId: string) => {
    const updateNode = (nodes: FileNode[]): FileNode[] => {
      return nodes.map(node => {
        if (node.id === nodeId && node.type === 'directory') {
          return { ...node, isExpanded: !node.isExpanded };
        }
        if (node.children) {
          return { ...node, children: updateNode(node.children) };
        }
        return node;
      });
    };

    setFileTree(updateNode(fileTree));
  };

  const selectFile = (file: FileNode) => {
    if (hasUnsavedChanges) {
      if (!confirm('You have unsaved changes. Do you want to discard them?')) {
        return;
      }
    }

    setSelectedFile(file);
    if (file.type === 'file' && file.content !== undefined) {
      setFileContent(file.content);
      setEditingFile(file);
      setIsEditing(false);
      setHasUnsavedChanges(false);
    }
  };

  const startEditing = () => {
    setIsEditing(true);
  };

  const saveFile = () => {
    if (!editingFile) return;

    // Update the file content in the tree
    const updateFileContent = (nodes: FileNode[]): FileNode[] => {
      return nodes.map(node => {
        if (node.id === editingFile.id) {
          return { ...node, content: fileContent, modified: new Date().toISOString() };
        }
        if (node.children) {
          return { ...node, children: updateFileContent(node.children) };
        }
        return node;
      });
    };

    setFileTree(updateFileContent(fileTree));
    setHasUnsavedChanges(false);
    setIsEditing(false);
    
    // Show success message
    alert('File saved successfully!');
  };

  const cancelEditing = () => {
    if (hasUnsavedChanges) {
      if (!confirm('You have unsaved changes. Do you want to discard them?')) {
        return;
      }
    }
    
    if (editingFile && editingFile.content !== undefined) {
      setFileContent(editingFile.content);
    }
    setIsEditing(false);
    setHasUnsavedChanges(false);
  };

  const handleContentChange = (value: string) => {
    setFileContent(value);
    setHasUnsavedChanges(true);
  };

  const createNewFile = () => {
    const fileName = prompt('Enter file name:');
    if (!fileName) return;

    const newFile: FileNode = {
      id: Date.now().toString(),
      name: fileName,
      type: 'file',
      path: `/${fileName}`,
      size: 0,
      modified: new Date().toISOString(),
      content: ''
    };

    setFileTree([...fileTree, newFile]);
  };

  const deleteFile = (file: FileNode) => {
    if (!confirm(`Are you sure you want to delete ${file.name}?`)) {
      return;
    }

    const removeNode = (nodes: FileNode[]): FileNode[] => {
      return nodes.filter(node => {
        if (node.id === file.id) {
          return false;
        }
        if (node.children) {
          node.children = removeNode(node.children);
        }
        return true;
      });
    };

    setFileTree(removeNode(fileTree));
    
    if (selectedFile?.id === file.id) {
      setSelectedFile(null);
      setEditingFile(null);
      setFileContent('');
      setIsEditing(false);
      setHasUnsavedChanges(false);
    }
  };

  const renderFileTree = (nodes: FileNode[], depth = 0) => {
    return nodes
      .filter(node => 
        searchTerm === '' || 
        node.name.toLowerCase().includes(searchTerm.toLowerCase())
      )
      .map(node => (
        <div key={node.id}>
          <div
            className={`flex items-center gap-2 px-2 py-1 hover:bg-gray-100 cursor-pointer rounded ${
              selectedFile?.id === node.id ? 'bg-blue-50 text-blue-700' : ''
            }`}
            style={{ paddingLeft: `${depth * 20 + 8}px` }}
            onClick={() => {
              if (node.type === 'directory') {
                toggleDirectory(node.id);
              } else {
                selectFile(node);
              }
            }}
          >
            {node.type === 'directory' && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  toggleDirectory(node.id);
                }}
                className="p-0.5 hover:bg-gray-200 rounded"
              >
                {node.isExpanded ? (
                  <ChevronDown className="h-3 w-3" />
                ) : (
                  <ChevronRight className="h-3 w-3" />
                )}
              </button>
            )}
            
            {getFileIcon(node)}
            
            <span className="flex-1 text-sm">{node.name}</span>
            
            {node.type === 'file' && (
              <div className="flex items-center gap-1">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    selectFile(node);
                    startEditing();
                  }}
                  className="p-1 hover:bg-gray-200 rounded opacity-0 group-hover:opacity-100"
                  title="Edit file"
                >
                  <Edit3 className="h-3 w-3" />
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteFile(node);
                  }}
                  className="p-1 hover:bg-red-200 rounded opacity-0 group-hover:opacity-100"
                  title="Delete file"
                >
                  <Trash2 className="h-3 w-3 text-red-600" />
                </button>
              </div>
            )}
          </div>
          
          {node.type === 'directory' && node.isExpanded && node.children && (
            <div>
              {renderFileTree(node.children, depth + 1)}
            </div>
          )}
        </div>
      ));
  };

  const formatFileSize = (bytes: number) => {
    const units = ['B', 'KB', 'MB', 'GB'];
    let size = bytes;
    let unitIndex = 0;
    
    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024;
      unitIndex++;
    }
    
    return `${size.toFixed(1)} ${units[unitIndex]}`;
  };

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey || e.metaKey) {
        switch (e.key) {
          case 's':
            e.preventDefault();
            if (isEditing && hasUnsavedChanges) {
              saveFile();
            }
            break;
          case 'Escape':
            if (isEditing) {
              cancelEditing();
            }
            break;
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isEditing, hasUnsavedChanges]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">File Explorer & Editor</h2>
        <p className="text-gray-600 mt-1">
          Browse, view, and edit files directly in your browser
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-200px)]">
        {/* File Tree */}
        <div className="card p-4 overflow-hidden flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Files</h3>
            <button
              onClick={createNewFile}
              className="btn-outline text-sm flex items-center gap-2"
            >
              <Plus className="h-4 w-4" />
              New File
            </button>
          </div>
          
          {/* Search */}
          <div className="relative mb-4">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search files..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input pl-10"
            />
          </div>
          
          {/* File Tree */}
          <div className="flex-1 overflow-y-auto">
            <div className="space-y-1 group">
              {renderFileTree(fileTree)}
            </div>
          </div>
        </div>

        {/* File Content/Editor */}
        <div className="lg:col-span-2 card p-4 overflow-hidden flex flex-col">
          {selectedFile ? (
            <>
              {/* File Header */}
              <div className="flex items-center justify-between mb-4 pb-4 border-b border-gray-200">
                <div className="flex items-center gap-3">
                  {getFileIcon(selectedFile)}
                  <div>
                    <h3 className="font-semibold">{selectedFile.name}</h3>
                    <p className="text-sm text-gray-500">
                      {selectedFile.size && formatFileSize(selectedFile.size)} • 
                      Modified {selectedFile.modified && new Date(selectedFile.modified).toLocaleString()}
                    </p>
                  </div>
                  {hasUnsavedChanges && (
                    <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">
                      Unsaved changes
                    </span>
                  )}
                </div>
                
                <div className="flex items-center gap-2">
                  {isEditing ? (
                    <>
                      <button
                        onClick={saveFile}
                        className="btn-primary text-sm flex items-center gap-2"
                        disabled={!hasUnsavedChanges}
                      >
                        <Save className="h-4 w-4" />
                        Save
                      </button>
                      <button
                        onClick={cancelEditing}
                        className="btn-secondary text-sm flex items-center gap-2"
                      >
                        <X className="h-4 w-4" />
                        Cancel
                      </button>
                    </>
                  ) : (
                    <button
                      onClick={startEditing}
                      className="btn-outline text-sm flex items-center gap-2"
                    >
                      <Edit3 className="h-4 w-4" />
                      Edit
                    </button>
                  )}
                </div>
              </div>
              
              {/* File Content */}
              <div className="flex-1 overflow-hidden">
                {isEditing ? (
                  <textarea
                    value={fileContent}
                    onChange={(e) => handleContentChange(e.target.value)}
                    className="w-full h-full p-4 border border-gray-300 rounded-lg font-mono text-sm resize-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Enter file content..."
                  />
                ) : (
                  <pre className="w-full h-full p-4 bg-gray-50 border border-gray-200 rounded-lg overflow-auto font-mono text-sm whitespace-pre-wrap">
                    {fileContent || 'No content to display'}
                  </pre>
                )}
              </div>
              
              {/* Editor Help */}
              {isEditing && (
                <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <p className="text-sm text-blue-800">
                    <strong>Keyboard shortcuts:</strong> Ctrl+S to save, Esc to cancel editing
                  </p>
                </div>
              )}
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center text-gray-500">
              <div className="text-center">
                <File className="h-16 w-16 mx-auto mb-4 opacity-50" />
                <p className="text-lg font-medium">No file selected</p>
                <p className="text-sm">Select a file from the tree to view its content</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Help */}
      <div className="card p-6 bg-green-50 border-green-200">
        <h3 className="text-lg font-semibold text-green-900 mb-2">File Explorer Help</h3>
        <div className="text-sm text-green-800 space-y-2">
          <p><strong>Navigation:</strong> Click on folders to expand/collapse, click on files to view content</p>
          <p><strong>Editing:</strong> Click "Edit" to modify files, use Ctrl+S to save changes</p>
          <p><strong>Search:</strong> Use the search box to quickly find files by name</p>
          <p><strong>File Management:</strong> Create new files with the "New File" button</p>
          <p><strong>File Types:</strong> Different icons indicate file types (code, styles, images, etc.)</p>
        </div>
      </div>
    </div>
  );
};

export default FileExplorerTab;