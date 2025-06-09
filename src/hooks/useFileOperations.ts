import { useState, useCallback } from 'react';

export interface FileItem {
  id: string;
  name: string;
  path: string;
  size: number;
  type: string;
  modified: string;
  isDirectory?: boolean;
}

export interface DirectoryStructureItem {
  path: string;
  type: 'file' | 'directory';
  depth: number;
  name: string;
}

export interface Operation {
  id: string;
  type: string;
  timestamp: string;
  details: string;
  status: 'success' | 'error' | 'pending';
  actions?: any[];
}

export const useFileOperations = () => {
  const [operations, setOperations] = useState<Operation[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);

  const addOperation = useCallback((operation: Omit<Operation, 'id' | 'timestamp'>) => {
    const newOperation: Operation = {
      ...operation,
      id: Date.now().toString(),
      timestamp: new Date().toISOString(),
    };
    setOperations(prev => [newOperation, ...prev]);
    return newOperation.id;
  }, []);

  const updateOperation = useCallback((id: string, updates: Partial<Operation>) => {
    setOperations(prev => prev.map(op => 
      op.id === id ? { ...op, ...updates } : op
    ));
  }, []);

  const parseStructureDefinition = useCallback((definition: string): DirectoryStructureItem[] => {
    const lines = definition.split('\n').filter(line => line.trim() && !line.trim().startsWith('#'));
    const items: DirectoryStructureItem[] = [];

    lines.forEach(line => {
      const leadingSpaces = line.length - line.trimStart().length;
      const depth = Math.floor(leadingSpaces / 2);
      const name = line.trim();
      const isDirectory = name.endsWith('/');
      const cleanName = name.replace(/\/$/, '');

      if (cleanName) {
        items.push({
          path: cleanName,
          type: isDirectory ? 'directory' : 'file',
          depth,
          name: cleanName
        });
      }
    });

    return items;
  }, []);

  const simulateFileOperation = useCallback(async (
    operationType: string,
    items: any[],
    onProgress?: (progress: number, message: string) => void
  ) => {
    setIsProcessing(true);
    const operationId = addOperation({
      type: operationType,
      details: `Processing ${items.length} items`,
      status: 'pending'
    });

    try {
      for (let i = 0; i < items.length; i++) {
        // Simulate processing time
        await new Promise(resolve => setTimeout(resolve, 100 + Math.random() * 200));
        
        const progress = ((i + 1) / items.length) * 100;
        const message = `Processing ${i + 1}/${items.length}: ${items[i].name || items[i].path || 'item'}`;
        
        onProgress?.(progress, message);
      }

      updateOperation(operationId, {
        status: 'success',
        details: `Successfully processed ${items.length} items`
      });

      return { success: true, processedCount: items.length };
    } catch (error) {
      updateOperation(operationId, {
        status: 'error',
        details: `Failed: ${error instanceof Error ? error.message : 'Unknown error'}`
      });
      return { success: false, error };
    } finally {
      setIsProcessing(false);
    }
  }, [addOperation, updateOperation]);

  const createStructure = useCallback(async (
    definition: string,
    baseDirectory: string,
    onProgress?: (progress: number, message: string) => void
  ) => {
    const items = parseStructureDefinition(definition);
    return simulateFileOperation('create_structure', items, onProgress);
  }, [parseStructureDefinition, simulateFileOperation]);

  const moveFiles = useCallback(async (
    files: FileItem[],
    targetDirectory: string,
    onProgress?: (progress: number, message: string) => void
  ) => {
    return simulateFileOperation('move_files', files, onProgress);
  }, [simulateFileOperation]);

  const organizeFiles = useCallback(async (
    assignments: Array<{ source: FileItem; target: string }>,
    baseDirectory: string,
    operation: 'copy' | 'move',
    onProgress?: (progress: number, message: string) => void
  ) => {
    return simulateFileOperation(`organize_${operation}`, assignments, onProgress);
  }, [simulateFileOperation]);

  const createPackage = useCallback(async (
    assignments: Array<{ source: FileItem; target: string }>,
    packageName: string,
    onProgress?: (progress: number, message: string) => void
  ) => {
    const result = await simulateFileOperation('create_package', assignments, onProgress);
    
    if (result.success) {
      // Simulate package download
      const blob = new Blob(['# Package Contents\n\nThis is a simulated package file.'], 
        { type: 'application/zip' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${packageName}.zip`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }

    return result;
  }, [simulateFileOperation]);

  const undoLastOperation = useCallback(() => {
    const lastOperation = operations.find(op => op.status === 'success');
    if (!lastOperation) return false;

    // Simulate undo
    addOperation({
      type: 'undo',
      details: `Undoing: ${lastOperation.type}`,
      status: 'success'
    });

    return true;
  }, [operations, addOperation]);

  return {
    operations,
    isProcessing,
    createStructure,
    moveFiles,
    organizeFiles,
    createPackage,
    undoLastOperation,
    parseStructureDefinition,
    addOperation,
    updateOperation
  };
};