import React, { createContext, useContext, useState, ReactNode } from 'react';

interface Operation {
  id: string;
  operation: string;
  details: string;
  status: 'success' | 'error' | 'pending';
  timestamp: string;
}

interface DirectoryContextType {
  currentStructure: string;
  setCurrentStructure: (structure: string) => void;
  operations: Operation[];
  addOperation: (operation: Omit<Operation, 'id' | 'timestamp'>) => void;
}

const DirectoryContext = createContext<DirectoryContextType | undefined>(undefined);

export const useDirectory = () => {
  const context = useContext(DirectoryContext);
  if (context === undefined) {
    throw new Error('useDirectory must be used within a DirectoryProvider');
  }
  return context;
};

interface DirectoryProviderProps {
  children: ReactNode;
}

export const DirectoryProvider: React.FC<DirectoryProviderProps> = ({ children }) => {
  const [currentStructure, setCurrentStructure] = useState('');
  const [operations, setOperations] = useState<Operation[]>([]);

  const addOperation = (operation: Omit<Operation, 'id' | 'timestamp'>) => {
    const newOperation: Operation = {
      ...operation,
      id: Date.now().toString(),
      timestamp: new Date().toISOString(),
    };
    setOperations(prev => [newOperation, ...prev]);
  };

  return (
    <DirectoryContext.Provider
      value={{
        currentStructure,
        setCurrentStructure,
        operations,
        addOperation,
      }}
    >
      {children}
    </DirectoryContext.Provider>
  );
};