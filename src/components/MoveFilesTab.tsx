import React, { useState } from 'react';
import { Upload, Trash2, FolderOpen } from 'lucide-react';

interface FileItem {
  id: string;
  name: string;
  path: string;
  size: string;
  type: string;
}

const MoveFilesTab: React.FC = () => {
  const [files, setFiles] = useState<FileItem[]>([]);
  const [targetDirectory, setTargetDirectory] = useState('/target');

  const addSampleFiles = () => {
    const sampleFiles: FileItem[] = [
      {
        id: '1',
        name: 'document.pdf',
        path: '/source/document.pdf',
        size: '2.5 MB',
        type: 'PDF'
      },
      {
        id: '2',
        name: 'image.jpg',
        path: '/source/image.jpg',
        size: '1.2 MB',
        type: 'Image'
      },
      {
        id: '3',
        name: 'script.js',
        path: '/source/script.js',
        size: '15 KB',
        type: 'JavaScript'
      }
    ];
    setFiles([...files, ...sampleFiles]);
  };

  const clearFiles = () => {
    setFiles([]);
  };

  const moveFiles = () => {
    if (files.length === 0) {
      alert('No files selected to move');
      return;
    }
    alert(`Moving ${files.length} files to ${targetDirectory}`);
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Quick Move Files</h2>
        <p className="text-gray-600 mt-1">
          Select files and move them to a target directory
        </p>
      </div>

      <div className="card p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">Files to Move</h3>
          <div className="flex gap-2">
            <button
              onClick={addSampleFiles}
              className="btn-outline text-sm flex items-center gap-2"
            >
              <Upload className="h-4 w-4" />
              Add Sample Files
            </button>
            <button
              onClick={clearFiles}
              className="btn-secondary text-sm flex items-center gap-2"
            >
              <Trash2 className="h-4 w-4" />
              Clear List
            </button>
          </div>
        </div>

        <div className="border border-gray-200 rounded-lg overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">File Name</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Path</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Size</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Type</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {files.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-4 py-8 text-center text-gray-500">
                    No files selected. Click "Add Sample Files" to get started.
                  </td>
                </tr>
              ) : (
                files.map((file) => (
                  <tr key={file.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">{file.name}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">{file.path}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">{file.size}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">{file.type}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div className="card p-6">
        <h3 className="text-lg font-semibold mb-4">Target Directory</h3>
        <div className="flex gap-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Destination Path
            </label>
            <input
              type="text"
              value={targetDirectory}
              onChange={(e) => setTargetDirectory(e.target.value)}
              className="input w-full"
              placeholder="/path/to/target/directory"
            />
          </div>
          <div className="flex items-end">
            <button className="btn-outline flex items-center gap-2">
              <FolderOpen className="h-4 w-4" />
              Browse
            </button>
          </div>
        </div>
      </div>

      <div className="flex justify-between items-center">
        <div className="text-sm text-gray-600">
          {files.length} file(s) selected
        </div>
        <button
          onClick={moveFiles}
          className="btn-primary"
          disabled={files.length === 0}
        >
          Move Selected Files
        </button>
      </div>
    </div>
  );
};

export default MoveFilesTab;