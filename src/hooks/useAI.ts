import { useState, useCallback } from 'react';

interface AIConfig {
  apiKey: string;
  model: string;
}

export const useAI = () => {
  const [config, setConfig] = useState<AIConfig>({
    apiKey: '',
    model: 'gemini-pro'
  });
  const [isLoading, setIsLoading] = useState(false);

  const updateConfig = useCallback((newConfig: Partial<AIConfig>) => {
    setConfig(prev => ({ ...prev, ...newConfig }));
    // Save to localStorage
    localStorage.setItem('ai-config', JSON.stringify({ ...config, ...newConfig }));
  }, [config]);

  const loadConfig = useCallback(() => {
    const saved = localStorage.getItem('ai-config');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setConfig(parsed);
      } catch (error) {
        console.error('Failed to load AI config:', error);
      }
    }
  }, []);

  const suggestStructure = useCallback(async (fileExtensions: string[]): Promise<string> => {
    if (!config.apiKey) {
      throw new Error('API key not configured');
    }

    setIsLoading(true);
    try {
      // Simulate AI response for structure suggestion
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const suggestions = {
        web: `project/
  src/
    components/
      Header.tsx
      Footer.tsx
    pages/
      Home.tsx
      About.tsx
    hooks/
      useAuth.ts
    utils/
      helpers.ts
    styles/
      globals.css
  public/
    images/
    icons/
  tests/
    components/
    pages/
  package.json
  README.md`,
        
        python: `my_package/
  src/
    my_package/
      __init__.py
      core.py
      utils.py
      models/
        __init__.py
        base.py
    tests/
      __init__.py
      test_core.py
      test_utils.py
  docs/
    index.md
    api.md
  setup.py
  requirements.txt
  README.md`,
        
        general: `project/
  src/
    main/
    utils/
  docs/
    README.md
  tests/
  config/
  data/
    input/
    output/`
      };

      // Determine project type based on extensions
      const hasWebExtensions = fileExtensions.some(ext => 
        ['.js', '.ts', '.jsx', '.tsx', '.css', '.scss', '.html'].includes(ext)
      );
      const hasPythonExtensions = fileExtensions.some(ext => 
        ['.py', '.pyx', '.pyi'].includes(ext)
      );

      if (hasWebExtensions) return suggestions.web;
      if (hasPythonExtensions) return suggestions.python;
      return suggestions.general;

    } finally {
      setIsLoading(false);
    }
  }, [config.apiKey]);

  const summarizeCode = useCallback(async (code: string, fileName: string): Promise<string> => {
    if (!config.apiKey) {
      throw new Error('API key not configured');
    }

    setIsLoading(true);
    try {
      // Simulate AI response for code summary
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      const extension = fileName.split('.').pop()?.toLowerCase();
      
      const summaries = {
        'ts': `This TypeScript file appears to be a React component or utility module. It likely contains type definitions, interfaces, and functions that handle specific business logic or UI interactions.`,
        'tsx': `This is a React component written in TypeScript. It defines a reusable UI component with props, state management, and event handlers. The component follows modern React patterns and includes proper type safety.`,
        'js': `This JavaScript file contains functions and logic for handling specific application features. It may include utility functions, API calls, or business logic implementations.`,
        'py': `This Python file contains class definitions, functions, and logic for handling specific application functionality. It follows Python best practices and may include data processing, API endpoints, or utility functions.`,
        'css': `This CSS file contains styling rules and layout definitions. It includes responsive design patterns, color schemes, and visual styling for UI components.`
      };

      return summaries[extension as keyof typeof summaries] || 
        `This ${extension || 'code'} file contains implementation logic and follows standard coding practices for its language. It appears to be well-structured and serves a specific purpose within the application architecture.`;

    } finally {
      setIsLoading(false);
    }
  }, [config.apiKey]);

  const suggestImprovements = useCallback(async (code: string, fileName: string): Promise<string> => {
    if (!config.apiKey) {
      throw new Error('API key not configured');
    }

    setIsLoading(true);
    try {
      // Simulate AI response for code improvements
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      return `## Code Improvement Suggestions for ${fileName}

### 1. Code Structure & Organization
- Consider breaking down large functions into smaller, more focused functions
- Group related functionality into modules or classes
- Use consistent naming conventions throughout the file

### 2. Performance Optimizations
- Look for opportunities to memoize expensive calculations
- Consider lazy loading for heavy imports
- Optimize loops and data structures where possible

### 3. Error Handling
- Add comprehensive error handling with try-catch blocks
- Validate input parameters and provide meaningful error messages
- Consider edge cases and handle them gracefully

### 4. Code Quality
- Add JSDoc comments for better documentation
- Use TypeScript for better type safety (if not already)
- Consider using linting tools like ESLint for consistency

### 5. Testing
- Add unit tests for critical functions
- Consider integration tests for complex workflows
- Use test-driven development for new features

### 6. Security
- Validate and sanitize user inputs
- Use secure coding practices for data handling
- Keep dependencies updated to avoid vulnerabilities`;

    } finally {
      setIsLoading(false);
    }
  }, [config.apiKey]);

  return {
    config,
    isLoading,
    updateConfig,
    loadConfig,
    suggestStructure,
    summarizeCode,
    suggestImprovements
  };
};