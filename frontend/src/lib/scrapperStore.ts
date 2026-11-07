import { create } from 'zustand';

export interface ScraperTask {
  id: string;
  name: string;
  status: 'running' | 'idle' | 'complete';
  progress: number;
  message: string;
  timestamp: Date;
}

interface ScrapperStore {
  tasks: ScraperTask[];
  addTask: (task: ScraperTask) => void;
  updateTask: (id: string, updates: Partial<ScraperTask>) => void;
  removeTask: (id: string) => void;
  clearTasks: () => void;
  getActiveTasks: () => ScraperTask[];
}

export const useScrapperStore = create<ScrapperStore>((set, get) => ({
  tasks: [],
  
  addTask: (task: ScraperTask) => set((state) => ({
    tasks: [...state.tasks, task],
  })),
  
  updateTask: (id: string, updates: Partial<ScraperTask>) => set((state) => ({
    tasks: state.tasks.map((t) => t.id === id ? { ...t, ...updates } : t),
  })),
  
  removeTask: (id: string) => set((state) => ({
    tasks: state.tasks.filter((t) => t.id !== id),
  })),
  
  clearTasks: () => set({ tasks: [] }),
  
  getActiveTasks: () => get().tasks.filter((t) => t.status === 'running'),
}));
