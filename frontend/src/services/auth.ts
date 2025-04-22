import { User } from '../types';

// Mock delay to simulate API call
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// Mock user data
const MOCK_USERS = [
  {
    id: '1',
    email: 'user@example.com',
    password: 'password123',
    name: 'Demo User'
  }
];

export const login = async (email: string, password: string): Promise<User> => {
  await delay(1000); // Simulate API delay
  
  const user = MOCK_USERS.find(u => u.email === email && u.password === password);
  
  if (user) {
    const { password, ...userWithoutPassword } = user;
    localStorage.setItem('isAuthenticated', 'true');
    localStorage.setItem('user', JSON.stringify(userWithoutPassword));
    return userWithoutPassword;
  }
  
  throw new Error('Invalid email or password');
};

export const register = async (name: string, email: string, password: string): Promise<User> => {
  await delay(1000); // Simulate API delay
  
  // Check if user already exists
  if (MOCK_USERS.some(u => u.email === email)) {
    throw new Error('User with this email already exists');
  }
  
  // In a real app, this would create a new user in the database
  // For now, we'll just simulate success
  const newUser = {
    id: Math.random().toString(36).substr(2, 9),
    name,
    email
  };
  
  localStorage.setItem('isAuthenticated', 'true');
  localStorage.setItem('user', JSON.stringify(newUser));
  
  return newUser;
};

export const logout = (): void => {
  localStorage.removeItem('isAuthenticated');
  localStorage.removeItem('user');
};

export const getCurrentUser = (): User | null => {
  const userJson = localStorage.getItem('user');
  return userJson ? JSON.parse(userJson) : null;
};

export const isAuthenticated = (): boolean => {
  return localStorage.getItem('isAuthenticated') === 'true';
};