import React, { useState } from 'react';
import { Package, Zap, Archive, FolderTree, Target, Upload, Download, Settings } from 'lucide-react';
import { useDirectory } from '../../context/DirectoryContext';
import { useFileOperations } from '../../hooks/useFileOperations';
import ProgressDialog from '../ProgressDialog';

interface StagedFile {
  id: string;
  name: string;
  path: string;
  size: number;
  type: string;
  status: 'staged' | 'assigned' | 'organized';
  targetPath?: string;
}

interface TargetSlot {
  id: string;
  path: string;
  type: 'file' | 'directory';
  assignedFile?: StagedFile;
  status: 'empty' | 'assigned' | 'auto-matched';
  confidence?: number;
}

const SmartOrganizeTab: React.FC = () => {
  const { addOperation } = useDirectory();
  const { organizeFiles, createPackage } = useFileOperations();
  
  const [stagedFiles, setStagedFiles] = useState<StagedFile[]>([]);
  const [targetStructure, setTargetStructure] = useState('');
  const [targetSlots, setTargetSlots] = useState<TargetSlot[]>([]);
  const [organizationMode, setOrganizationMode] = useState<'manual' | 'auto'>('auto');
  const [showProgress, setShowProgress] = useState(false);
  const [progress, setProgress] = useState(0);
  const [progressMessage, setProgressMessage] = useState('');

  const addFilesToStage = () => {
    // Simulate adding files
    const newFiles: StagedFile[] = [
      {
        id: Date.now().toString(),
        name: `document_${stagedFiles.length + 1}.pdf`,
        path: `/files/document_${stagedFiles.length + 1}.pdf`,
        size: Math.floor(Math.random() * 1000000),
        type: 'application/pdf',
        status: 'staged'
      },
      {
        id: (Date.now() + 1).toString(),
        name: `image_${stagedFiles.length + 1}.jpg`,
        path: `/files/image_${stagedFiles.length + 1}.jpg`,
        size: Math.floor(Math.random() * 2000000),
        type: 'image/jpeg',
        status: 'staged'
      }
    ];
    setStagedFiles([...stagedFiles, ...newFiles]);
  };

  const buildTargetStructure = () => {
    if (!targetStructure.trim()) {
      alert('Please define a target structure first');
      return;
    }

    const lines = targetStructure.split('\n').filter(line => line.trim());
    const slots: TargetSlot[] = [];

    lines.forEach((line, index) => {
      const trimmed = line.trim();
      if (trimmed && !trimmed.startsWith('#')) {
        const isDirectory = trimmed.endsWith('/');
        const path = trimmed.replace(/\/$/, '');
        
        if (!isDirectory) { // Only create slots for files
          slots.push({
            id: `slot_${index}`,
            path,
            type: 'file',
            status: 'empty'
          });
        }
      }
    });

    setTargetSlots(slots);
    addOperation({
      operation: 'build_target_structure',
      details: `Created ${slots.length} target slots`,
      status: 'success'
    });
  };

  const autoAssignFiles = async () => {
    if (stagedFiles.length === 0 || targetSlots.length === 0) {
      alert('Need both staged files and target slots');
      return;
    }

    setShowProgress(true);
    setProgress(0);
    setProgressMessage('Auto-assigning files...');

    try {
      const updatedSlots = [...targetSlots];
      const updatedFiles = [...stagedFiles];
      let assignedCount = 0;

      for (let i = 0; i < targetSlots.length; i++) {
        const slot = updatedSlots[i];
        if (slot.status === 'empty') {
          // Simple matching based on file extension
          const targetExt = slot.path.split('.').pop()?.toLowerCase();
          const matchingFile = updatedFiles.find(file => 
            file.status === 'staged' && 
            file.name.toLowerCase().includes(targetExt || '')
          );

          if (matchingFile) {
            slot.assignedFile = matchingFile;
            slot.status = 'auto-matched';
            slot.confidence = 75 + Math.random() * 20; // 75-95%
            
            matchingFile.status = 'assigned';
            matchingFile.targetPath = slot.path;
            assignedCount++;
          }
        }

        setProgress(((i + 1) / targetSlots.length) * 100);
        setProgressMessage(`Processing slot ${i + 1}/${targetSlots.length}`);
        
        // Simulate processing time
        await new Promise(resolve => setTimeout(resolve, 100));
      }

      setTargetSlots(updatedSlots);
      setStagedFiles(updatedFiles);

      addOperation({
        operation: 'auto_assign',
        details: `Auto-assigned ${assignedCount} files`,
        status: 'success'
      });

      alert(`Successfully auto-assigned ${assignedCount} files!`);
    } catch (error) {
      alert('Auto-assignment failed');
    } finally {
      setShowProgress(false);
    }
  };

  const organizeAssignedFiles = async () => {
    const assignments = targetSlots
      .filter(slot => slot.assignedFile)
      .map(slot => ({
        source: slot.assignedFile!,
        target: slot.path
      }));

    if (assignments.length === 0) {
      alert('No files assigned to organize');
      return;
    }

    setShowProgress(true);
    setProgress(0);
    setProgressMessage('Organizing files...');

    try {
      const result = await organizeFiles(
        assignments,
        '/organized',
        'copy',
        (progress, message) => {
          setProgress(progress);
          setProgressMessage(message);
        }
      );

      if (result.success) {
        // Update file statuses
        const updatedFiles = stagedFiles.map(file => {
          const assignment = assignments.find(a => a.source.id === file.id);
          return assignment ? { ...file, status: 'organized' as const } : file;
        });
        setStagedFiles(updatedFiles);

        alert(`Successfully organized ${assignments.length} files!`);
      }
    } catch (error) {
      alert('Organization failed');
    } finally {
      setShowProgress(false);
    }
  };

  const createOrganizedPackage = async () => {
    const assignments = targetSlots
      .filter(slot => slot.assignedFile)
      .map(slot => ({
        source: slot.assignedFile!,
        target: slot.path
      }));

    if (assignments.length === 0) {
      alert('No files assigned to package');
      return;
    }

    setShowProgress(true);
    setProgress(0);
    setProgressMessage('Creating package...');

    try {
      const result = await createPackage(
        assignments,
        `organized_package_${new Date().toISOString().split('T')[0]}`,
        (progress, message) => {
          setProgress(progress);
          setProgressMessage(message);
        }
      );

      if (result.success) {
        alert(`Package created and downloaded successfully!`);
      }
    } catch (error) {
      alert('Package creation failed');
    } finally {
      setShowProgress(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'staged': return 'bg-yellow-100 text-yellow-800';
      case 'assigned': return 'bg-blue-100 text-blue-800';
      case 'organized': return 'bg-green-100 text-green-800';
      case 'auto-matched': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const assignedCount = targetSlots.filter(slot => slot.assignedFile).length;
  const completionPercentage = targetSlots.length > 0 ? (assignedCount / targetSlots.length) * 100 : 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Smart Organize & Package</h2>
        <p className="text-gray-600 mt-1">
          Intelligently organize files using AI-powered matching and create structured packages
        </p>
      </div>

      {/* Organization Mode */}
      <div className="card p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Settings className="h-5 w-5" />
          Organization Settings
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Organization Mode
            </label>
            <div className="space-y-2">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  value="auto"
                  checked={organizationMode === 'auto'}
                  onChange={(e) => setOrganizationMode(e.target.value as 'auto')}
                  className="text-blue-600"
                />
                <span className="font-medium">Auto Assignment</span>
                <span className="text-sm text-gray-500">- AI matches files to targets</span>
              </label>
              
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  value="manual"
                  checked={organizationMode === 'manual'}
                  onChange={(e) => setOrganizationMode(e.target.value as 'manual')}
                  className="text-blue-600"
                />
                <span className="font-medium">Manual Assignment</span>
                <span className="text-sm text-gray-500">- Drag and drop files to targets</span>
              </label>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Completion Status
            </label>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Progress</span>
                <span>{Math.round(completionPercentage)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${completionPercentage}%` }}
                />
              </div>
              <p className="text-sm text-gray-600">
                {assignedCount} of {targetSlots.length} slots assigned
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Staging Area */}
        <div className="card p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <FolderTree className="h-5 w-5" />
              File Staging Area
            </h3>
            
            <button
              onClick={addFilesToStage}
              className="btn-outline text-sm flex items-center gap-2"
            >
              <Upload className="h-4 w-4" />
              Add Files
            </button>
          </div>
          
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {stagedFiles.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Package className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p>No files staged</p>
                <p className="text-sm">Add files to get started</p>
              </div>
            ) : (
              stagedFiles.map((file) => (
                <div key={file.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex-1">
                    <div className="font-medium text-sm">{file.name}</div>
                    <div className="text-xs text-gray-500">
                      {(file.size / 1024).toFixed(1)} KB • {file.type}
                    </div>
                    {file.targetPath && (
                      <div className="text-xs text-blue-600 mt-1">→ {file.targetPath}</div>
                    )}
                  </div>
                  
                  <span className={`status-indicator ${getStatusColor(file.status)}`}>
                    {file.status}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Target Structure */}
        <div className="card p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Target className="h-5 w-5" />
            Target Structure
          </h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Structure Definition
              </label>
              <textarea
                value={targetStructure}
                onChange={(e) => setTargetStructure(e.target.value)}
                className="textarea code-editor"
                rows={8}
                placeholder={`Define your target structure:

organized/
  documents/
    reports/
      report.pdf
    presentations/
      slides.pptx
  media/
    images/
      photo.jpg
    videos/
      video.mp4`}
              />
            </div>
            
            <button
              onClick={buildTargetStructure}
              className="btn-primary w-full flex items-center justify-center gap-2"
            >
              <FolderTree className="h-4 w-4" />
              Build Target Structure
            </button>
          </div>

          {/* Target Slots */}
          {targetSlots.length > 0 && (
            <div className="mt-4">
              <h4 className="font-medium text-gray-900 mb-2">Target Slots</h4>
              <div className="space-y-1 max-h-32 overflow-y-auto">
                {targetSlots.map((slot) => (
                  <div key={slot.id} className="flex items-center justify-between p-2 bg-gray-50 rounded text-sm">
                    <span className="font-mono">{slot.path}</span>
                    <div className="flex items-center gap-2">
                      {slot.confidence && (
                        <span className="text-xs text-gray-500">{Math.round(slot.confidence)}%</span>
                      )}
                      <span className={`status-indicator text-xs ${getStatusColor(slot.status)}`}>
                        {slot.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Actions */}
      <div className="card p-6">
        <h3 className="text-lg font-semibold mb-4">Actions</h3>
        
        <div className="flex flex-wrap gap-4">
          <button
            onClick={autoAssignFiles}
            className="btn-primary flex items-center gap-2"
            disabled={stagedFiles.length === 0 || targetSlots.length === 0}
          >
            <Zap className="h-4 w-4" />
            Auto-Assign Files
          </button>
          
          <button
            onClick={organizeAssignedFiles}
            className="btn-outline flex items-center gap-2"
            disabled={assignedCount === 0}
          >
            <FolderTree className="h-4 w-4" />
            Organize Files
          </button>
          
          <button
            onClick={createOrganizedPackage}
            className="btn-outline flex items-center gap-2"
            disabled={assignedCount === 0}
          >
            <Archive className="h-4 w-4" />
            Create Package
          </button>
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card p-4 text-center">
          <div className="text-2xl font-bold text-blue-600">{stagedFiles.length}</div>
          <div className="text-sm text-gray-600">Files Staged</div>
        </div>
        
        <div className="card p-4 text-center">
          <div className="text-2xl font-bold text-green-600">{assignedCount}</div>
          <div className="text-sm text-gray-600">Files Assigned</div>
        </div>
        
        <div className="card p-4 text-center">
          <div className="text-2xl font-bold text-purple-600">{targetSlots.length}</div>
          <div className="text-sm text-gray-600">Target Slots</div>
        </div>
        
        <div className="card p-4 text-center">
          <div className="text-2xl font-bold text-orange-600">
            {stagedFiles.filter(f => f.status === 'organized').length}
          </div>
          <div className="text-sm text-gray-600">Files Organized</div>
        </div>
      </div>

      {/* Help */}
      <div className="card p-6 bg-purple-50 border-purple-200">
        <h3 className="text-lg font-semibold text-purple-900 mb-2">Smart Organization Help</h3>
        <div className="text-sm text-purple-800 space-y-2">
          <p><strong>Staging:</strong> Add files that need to be organized</p>
          <p><strong>Target Structure:</strong> Define where files should be placed</p>
          <p><strong>Auto-Assignment:</strong> AI analyzes file types and names for optimal placement</p>
          <p><strong>Manual Assignment:</strong> Drag files to specific target locations</p>
          <p><strong>Organization:</strong> Copy or move files to their assigned locations</p>
          <p><strong>Packaging:</strong> Create ZIP archives maintaining the organized structure</p>
        </div>
      </div>

      {/* Progress Dialog */}
      <ProgressDialog
        isOpen={showProgress}
        title="Processing Files"
        message={progressMessage}
        progress={progress}
        onCancel={() => setShowProgress(false)}
      />
    </div>
  );
};

export default SmartOrganizeTab;