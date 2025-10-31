import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ProjectForm } from '../../src/components/projects/ProjectForm';
import { projectService } from '../../src/api_services/projectService';
import toast from 'react-hot-toast';

// Mock the projectService
vi.mock('../../src/api_services/projectService', () => ({
  projectService: {
    createProject: vi.fn(),
    updateProject: vi.fn(),
  },
}));

// Mock react-hot-toast
vi.mock('react-hot-toast', () => ({
  default: {
    error: vi.fn(),
    success: vi.fn(),
  },
}));

describe('ProjectForm', () => {
  const mockOnSuccess = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  // ========== BASIC RENDERING TESTS ==========

  it('renders project form fields', () => {
    render(<ProjectForm onSuccess={mockOnSuccess} />);
    
    expect(screen.getByLabelText(/project name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /create project/i })).toBeInTheDocument();
  });

  it('shows required asterisk on project name field', () => {
    render(<ProjectForm onSuccess={mockOnSuccess} />);
    
    const nameLabel = screen.getByText(/project name \*/i);
    expect(nameLabel).toBeInTheDocument();
  });

  it('has correct placeholder text', () => {
    render(<ProjectForm onSuccess={mockOnSuccess} />);
    
    const nameInput = screen.getByPlaceholderText(/enter project name/i);
    const descInput = screen.getByPlaceholderText(/enter project description \(optional\)/i);
    
    expect(nameInput).toBeInTheDocument();
    expect(descInput).toBeInTheDocument();
  });

  // ========== VALIDATION TESTS ==========

  it('shows validation error for empty project name', async () => {
    render(<ProjectForm onSuccess={mockOnSuccess} />);
    
    const submitButton = screen.getByRole('button', { name: /create project/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/project name is required/i)).toBeInTheDocument();
    });
  });

  it('shows validation error for project name with only whitespace', async () => {
    render(<ProjectForm onSuccess={mockOnSuccess} />);
    
    const nameInput = screen.getByLabelText(/project name/i);
    fireEvent.change(nameInput, { target: { value: '   ' } });
    
    const submitButton = screen.getByRole('button', { name: /create project/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/project name is required/i)).toBeInTheDocument();
    });
  });

  it('does not show validation error when project name is provided', async () => {
    projectService.createProject.mockResolvedValue({ 
      id: 1, 
      name: 'Test Project',
      description: '' 
    });

    render(<ProjectForm onSuccess={mockOnSuccess} />);
    
    const nameInput = screen.getByLabelText(/project name/i);
    fireEvent.change(nameInput, { target: { value: 'Test Project' } });
    
    const submitButton = screen.getByRole('button', { name: /create project/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.queryByText(/project name is required/i)).not.toBeInTheDocument();
    });
  });

  it('allows description to be optional', async () => {
    projectService.createProject.mockResolvedValue({ 
      id: 1, 
      name: 'Test Project',
      description: '' 
    });
    
    render(<ProjectForm onSuccess={mockOnSuccess} />);
    
    const nameInput = screen.getByLabelText(/project name/i);
    const descInput = screen.getByLabelText(/description/i);
    
    fireEvent.change(nameInput, { target: { value: 'Test Project' } });
    
    // Description should be empty
    expect(descInput.value).toBe('');
    
    const submitButton = screen.getByRole('button', { name: /create project/i });
    fireEvent.click(submitButton);
    
    // Should not show validation error for empty description
    await waitFor(() => {
      expect(screen.queryByText(/description is required/i)).not.toBeInTheDocument();
    });
  });

  it('applies error styling to name field when there is an error', async () => {
    render(<ProjectForm onSuccess={mockOnSuccess} />);
    
    const submitButton = screen.getByRole('button', { name: /create project/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      const nameInput = screen.getByLabelText(/project name/i);
      expect(nameInput.className).toContain('border-red-300');
    });
  });

  // ========== INPUT HANDLING TESTS ==========

  it('accepts valid input', () => {
    render(<ProjectForm onSuccess={mockOnSuccess} />);
    
    const nameInput = screen.getByLabelText(/project name/i);
    const descInput = screen.getByLabelText(/description/i);
    
    fireEvent.change(nameInput, { target: { value: 'Test Project' } });
    fireEvent.change(descInput, { target: { value: 'Test Description' } });
    
    expect(nameInput.value).toBe('Test Project');
    expect(descInput.value).toBe('Test Description');
  });

  it('updates form data when inputs change', () => {
    render(<ProjectForm onSuccess={mockOnSuccess} />);
    
    const nameInput = screen.getByLabelText(/project name/i);
    
    fireEvent.change(nameInput, { target: { value: 'First Name' } });
    expect(nameInput.value).toBe('First Name');
    
    fireEvent.change(nameInput, { target: { value: 'Updated Name' } });
    expect(nameInput.value).toBe('Updated Name');
  });

  // ========== FORM SUBMISSION TESTS ==========

  it('calls projectService.createProject with correct data', async () => {
    projectService.createProject.mockResolvedValue({
      id: 1,
      name: 'Test Project',
      description: 'Test Description',
    });
    
    render(<ProjectForm onSuccess={mockOnSuccess} />);
    
    const nameInput = screen.getByLabelText(/project name/i);
    const descInput = screen.getByLabelText(/description/i);
    
    fireEvent.change(nameInput, { target: { value: 'Test Project' } });
    fireEvent.change(descInput, { target: { value: 'Test Description' } });
    
    const submitButton = screen.getByRole('button', { name: /create project/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(projectService.createProject).toHaveBeenCalledWith({
        name: 'Test Project',
        description: 'Test Description',
      });
    });
  });

  it('calls onSuccess callback after successful submission', async () => {
    const mockProject = {
      id: 1,
      name: 'Test Project',
      description: 'Test Description',
    };
    
    projectService.createProject.mockResolvedValue(mockProject);
    
    render(<ProjectForm onSuccess={mockOnSuccess} />);
    
    const nameInput = screen.getByLabelText(/project name/i);
    fireEvent.change(nameInput, { target: { value: 'Test Project' } });
    
    const submitButton = screen.getByRole('button', { name: /create project/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(mockOnSuccess).toHaveBeenCalledWith(mockProject);
    });
  });

  it('disables submit button while loading', async () => {
    projectService.createProject.mockImplementation(() => 
      new Promise(resolve => setTimeout(() => resolve({ id: 1 }), 100))
    );
    
    render(<ProjectForm onSuccess={mockOnSuccess} />);
    
    const nameInput = screen.getByLabelText(/project name/i);
    fireEvent.change(nameInput, { target: { value: 'Test Project' } });
    
    const submitButton = screen.getByRole('button', { name: /create project/i });
    fireEvent.click(submitButton);
    
    // Button should be disabled during submission
    await waitFor(() => {
      expect(submitButton).toBeDisabled();
    });
    
    // Wait for the submission to complete to avoid affecting next test
    await waitFor(() => {
      expect(mockOnSuccess).toHaveBeenCalled();
    });
  });

  it('shows "Saving..." text while loading', async () => {
    projectService.createProject.mockImplementation(() => 
      new Promise(resolve => setTimeout(() => resolve({ id: 1 }), 100))
    );
    
    render(<ProjectForm onSuccess={mockOnSuccess} />);
    
    const nameInput = screen.getByLabelText(/project name/i);
    fireEvent.change(nameInput, { target: { value: 'Test Project' } });
    
    const submitButton = screen.getByRole('button', { name: /create project/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/saving.../i)).toBeInTheDocument();
    });
    
    // Wait for the submission to complete to avoid affecting next test
    await waitFor(() => {
      expect(mockOnSuccess).toHaveBeenCalled();
    });
  });

  it('shows error toast on submission failure', async () => {
    projectService.createProject.mockRejectedValue(new Error('API Error'));
    
    render(<ProjectForm onSuccess={mockOnSuccess} />);
    
    const nameInput = screen.getByLabelText(/project name/i);
    fireEvent.change(nameInput, { target: { value: 'Test Project' } });
    
    const submitButton = screen.getByRole('button', { name: /create project/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('Failed to save project');
    });
  });

  it('does not call onSuccess on submission failure', async () => {
    projectService.createProject.mockRejectedValue(new Error('API Error'));
    
    render(<ProjectForm onSuccess={mockOnSuccess} />);
    
    const nameInput = screen.getByLabelText(/project name/i);
    fireEvent.change(nameInput, { target: { value: 'Test Project' } });
    
    const submitButton = screen.getByRole('button', { name: /create project/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(toast.error).toHaveBeenCalled();
    });
    
    expect(mockOnSuccess).not.toHaveBeenCalled();
  });

  // ========== EDIT MODE TESTS ==========

  it('renders in edit mode with pre-filled data', () => {
    const existingProject = {
      id: 1,
      name: 'Existing Project',
      description: 'Existing Description',
    };
    
    render(<ProjectForm onSuccess={mockOnSuccess} initialData={existingProject} />);
    
    const nameInput = screen.getByLabelText(/project name/i);
    const descInput = screen.getByLabelText(/description/i);
    
    expect(nameInput.value).toBe('Existing Project');
    expect(descInput.value).toBe('Existing Description');
  });

  it('shows "Update Project" button text in edit mode', () => {
    const existingProject = {
      id: 1,
      name: 'Existing Project',
      description: 'Existing Description',
    };
    
    render(<ProjectForm onSuccess={mockOnSuccess} initialData={existingProject} />);
    
    expect(screen.getByRole('button', { name: /update project/i })).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /^create project$/i })).not.toBeInTheDocument();
  });

  it('calls projectService.updateProject in edit mode', async () => {
    const existingProject = {
      id: 1,
      name: 'Existing Project',
      description: 'Existing Description',
    };
    
    projectService.updateProject.mockResolvedValue({
      ...existingProject,
      name: 'Updated Project',
    });
    
    render(<ProjectForm onSuccess={mockOnSuccess} initialData={existingProject} />);
    
    const nameInput = screen.getByLabelText(/project name/i);
    fireEvent.change(nameInput, { target: { value: 'Updated Project' } });
    
    const submitButton = screen.getByRole('button', { name: /update project/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(projectService.updateProject).toHaveBeenCalledWith(1, {
        name: 'Updated Project',
        description: 'Existing Description',
      });
    });
  });

  it('does not call createProject in edit mode', async () => {
    const existingProject = {
      id: 1,
      name: 'Existing Project',
      description: 'Existing Description',
    };
    
    projectService.updateProject.mockResolvedValue(existingProject);
    
    render(<ProjectForm onSuccess={mockOnSuccess} initialData={existingProject} />);
    
    const submitButton = screen.getByRole('button', { name: /update project/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(projectService.updateProject).toHaveBeenCalled();
    });
    
    expect(projectService.createProject).not.toHaveBeenCalled();
  });
});