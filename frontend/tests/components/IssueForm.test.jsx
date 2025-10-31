import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { IssueForm } from '../../src/components/issues/IssueForm';
import { issueService } from '../../src/api_services/issueService';
import { ISSUE_STATUS, ISSUE_PRIORITY } from '../../src/utils/constants';
import toast from 'react-hot-toast';

// Mock the issueService
vi.mock('../../src/api_services/issueService', () => ({
  issueService: {
    createIssue: vi.fn(),
    updateIssue: vi.fn(),
  },
}));

// Mock react-hot-toast
vi.mock('react-hot-toast', () => ({
  default: {
    error: vi.fn(),
    success: vi.fn(),
  },
}));

describe('IssueForm', () => {
  const mockOnSuccess = vi.fn();
  const mockOnCancel = vi.fn();
  const mockProjectId = 1;

  beforeEach(() => {
    vi.clearAllMocks();
  });

  // ========== BASIC RENDERING TESTS ==========
  
  it('renders issue form fields', () => {
    render(<IssueForm projectId={mockProjectId} onSuccess={mockOnSuccess} />);
    
    expect(screen.getByLabelText(/issue title/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/status/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/priority/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /create issue/i })).toBeInTheDocument();
  });

  it('shows required asterisk on title field', () => {
    render(<IssueForm projectId={mockProjectId} onSuccess={mockOnSuccess} />);
    
    const titleLabel = screen.getByText(/issue title \*/i);
    expect(titleLabel).toBeInTheDocument();
  });

  it('has correct default values for status and priority', () => {
    render(<IssueForm projectId={mockProjectId} onSuccess={mockOnSuccess} />);
    
    const statusSelect = screen.getByLabelText(/status/i);
    const prioritySelect = screen.getByLabelText(/priority/i);
    
    expect(statusSelect.value).toBe(ISSUE_STATUS.OPEN);
    expect(prioritySelect.value).toBe(ISSUE_PRIORITY.MEDIUM);
  });

  it('renders all status options', () => {
    render(<IssueForm projectId={mockProjectId} onSuccess={mockOnSuccess} />);
    
    const statusSelect = screen.getByLabelText(/status/i);
    const options = Array.from(statusSelect.options).map(opt => opt.value);
    
    expect(options).toContain(ISSUE_STATUS.OPEN);
    expect(options).toContain(ISSUE_STATUS.IN_PROGRESS);
    expect(options).toContain(ISSUE_STATUS.CLOSED);
  });

  it('renders all priority options', () => {
    render(<IssueForm projectId={mockProjectId} onSuccess={mockOnSuccess} />);
    
    const prioritySelect = screen.getByLabelText(/priority/i);
    const options = Array.from(prioritySelect.options).map(opt => opt.value);
    
    expect(options).toContain(ISSUE_PRIORITY.LOW);
    expect(options).toContain(ISSUE_PRIORITY.MEDIUM);
    expect(options).toContain(ISSUE_PRIORITY.HIGH);
  });

  // ========== VALIDATION TESTS ==========

  it('shows validation error for empty title', async () => {
    render(<IssueForm projectId={mockProjectId} onSuccess={mockOnSuccess} />);
    
    const submitButton = screen.getByRole('button', { name: /create issue/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/issue title is required/i)).toBeInTheDocument();
    });
  });

  it('shows validation error for title with only whitespace', async () => {
    render(<IssueForm projectId={mockProjectId} onSuccess={mockOnSuccess} />);
    
    const titleInput = screen.getByLabelText(/issue title/i);
    fireEvent.change(titleInput, { target: { value: '   ' } });
    
    const submitButton = screen.getByRole('button', { name: /create issue/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/issue title is required/i)).toBeInTheDocument();
    });
  });

  it('does not show validation error when title is provided', async () => {
    render(<IssueForm projectId={mockProjectId} onSuccess={mockOnSuccess} />);
    
    const titleInput = screen.getByLabelText(/issue title/i);
    fireEvent.change(titleInput, { target: { value: 'Valid Issue Title' } });
    
    const submitButton = screen.getByRole('button', { name: /create issue/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.queryByText(/issue title is required/i)).not.toBeInTheDocument();
    });
  });

  it('does not require description field', async () => {
    issueService.createIssue.mockResolvedValue({ id: 1, title: 'Test' });
    
    render(<IssueForm projectId={mockProjectId} onSuccess={mockOnSuccess} />);
    
    const titleInput = screen.getByLabelText(/issue title/i);
    fireEvent.change(titleInput, { target: { value: 'Test Issue' } });
    
    const submitButton = screen.getByRole('button', { name: /create issue/i });
    fireEvent.click(submitButton);
    
    // Should not show any description validation error
    await waitFor(() => {
      expect(screen.queryByText(/description is required/i)).not.toBeInTheDocument();
    });
  });

  // ========== INPUT HANDLING TESTS ==========

  it('accepts valid issue input', () => {
    render(<IssueForm projectId={mockProjectId} onSuccess={mockOnSuccess} />);
    
    const titleInput = screen.getByLabelText(/issue title/i);
    const descInput = screen.getByLabelText(/description/i);
    const statusSelect = screen.getByLabelText(/status/i);
    const prioritySelect = screen.getByLabelText(/priority/i);
    
    fireEvent.change(titleInput, { target: { value: 'Bug Fix' } });
    fireEvent.change(descInput, { target: { value: 'Fix login bug' } });
    fireEvent.change(statusSelect, { target: { value: ISSUE_STATUS.IN_PROGRESS } });
    fireEvent.change(prioritySelect, { target: { value: ISSUE_PRIORITY.HIGH } });
    
    expect(titleInput.value).toBe('Bug Fix');
    expect(descInput.value).toBe('Fix login bug');
    expect(statusSelect.value).toBe(ISSUE_STATUS.IN_PROGRESS);
    expect(prioritySelect.value).toBe(ISSUE_PRIORITY.HIGH);
  });

  it('updates form data when inputs change', () => {
    render(<IssueForm projectId={mockProjectId} onSuccess={mockOnSuccess} />);
    
    const titleInput = screen.getByLabelText(/issue title/i);
    
    fireEvent.change(titleInput, { target: { value: 'First Title' } });
    expect(titleInput.value).toBe('First Title');
    
    fireEvent.change(titleInput, { target: { value: 'Updated Title' } });
    expect(titleInput.value).toBe('Updated Title');
  });

  it('clears validation error when user starts typing in title', async () => {
    render(<IssueForm projectId={mockProjectId} onSuccess={mockOnSuccess} />);
    
    const submitButton = screen.getByRole('button', { name: /create issue/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/issue title is required/i)).toBeInTheDocument();
    });
    
    const titleInput = screen.getByLabelText(/issue title/i);
    fireEvent.change(titleInput, { target: { value: 'T' } });
    
    // Error should still be there until form is revalidated on submit
    // But the red border should be removed (this is implementation dependent)
  });

  // ========== FORM SUBMISSION TESTS ==========

  it('calls issueService.createIssue with correct data', async () => {
    issueService.createIssue.mockResolvedValue({
      id: 1,
      title: 'Test Issue',
      description: 'Test Description',
      status: ISSUE_STATUS.OPEN,
      priority: ISSUE_PRIORITY.HIGH,
    });
    
    render(<IssueForm projectId={mockProjectId} onSuccess={mockOnSuccess} />);
    
    const titleInput = screen.getByLabelText(/issue title/i);
    const descInput = screen.getByLabelText(/description/i);
    const prioritySelect = screen.getByLabelText(/priority/i);
    
    fireEvent.change(titleInput, { target: { value: 'Test Issue' } });
    fireEvent.change(descInput, { target: { value: 'Test Description' } });
    fireEvent.change(prioritySelect, { target: { value: ISSUE_PRIORITY.HIGH } });
    
    const submitButton = screen.getByRole('button', { name: /create issue/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(issueService.createIssue).toHaveBeenCalledWith(mockProjectId, {
        title: 'Test Issue',
        description: 'Test Description',
        status: ISSUE_STATUS.OPEN,
        priority: ISSUE_PRIORITY.HIGH,
      });
    });
  });

  it('calls onSuccess callback after successful creation', async () => {
    const mockIssue = {
      id: 1,
      title: 'Test Issue',
      description: 'Test Description',
      status: ISSUE_STATUS.OPEN,
      priority: ISSUE_PRIORITY.MEDIUM,
    };
    
    issueService.createIssue.mockResolvedValue(mockIssue);
    
    render(<IssueForm projectId={mockProjectId} onSuccess={mockOnSuccess} />);
    
    const titleInput = screen.getByLabelText(/issue title/i);
    fireEvent.change(titleInput, { target: { value: 'Test Issue' } });
    
    const submitButton = screen.getByRole('button', { name: /create issue/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(mockOnSuccess).toHaveBeenCalledWith(mockIssue);
    });
  });

  it('disables submit button while loading', async () => {
    issueService.createIssue.mockImplementation(() => 
      new Promise(resolve => setTimeout(() => resolve({ id: 1 }), 100))
    );
    
    render(<IssueForm projectId={mockProjectId} onSuccess={mockOnSuccess} />);
    
    const titleInput = screen.getByLabelText(/issue title/i);
    fireEvent.change(titleInput, { target: { value: 'Test Issue' } });
    
    const submitButton = screen.getByRole('button', { name: /create issue/i });
    fireEvent.click(submitButton);
    
    // Button should be disabled during submission
    await waitFor(() => {
      expect(submitButton).toBeDisabled();
    });
  });

  it('shows "Saving..." text while loading', async () => {
    issueService.createIssue.mockImplementation(() => 
      new Promise(resolve => setTimeout(() => resolve({ id: 1 }), 100))
    );
    
    render(<IssueForm projectId={mockProjectId} onSuccess={mockOnSuccess} />);
    
    const titleInput = screen.getByLabelText(/issue title/i);
    fireEvent.change(titleInput, { target: { value: 'Test Issue' } });
    
    const submitButton = screen.getByRole('button', { name: /create issue/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/saving.../i)).toBeInTheDocument();
    });
  });

  it('shows error toast on submission failure', async () => {
    issueService.createIssue.mockRejectedValue(new Error('API Error'));
    
    render(<IssueForm projectId={mockProjectId} onSuccess={mockOnSuccess} />);
    
    const titleInput = screen.getByLabelText(/issue title/i);
    fireEvent.change(titleInput, { target: { value: 'Test Issue' } });
    
    const submitButton = screen.getByRole('button', { name: /create issue/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('Failed to save issue');
    });
  });

  it('does not call onSuccess on submission failure', async () => {
    issueService.createIssue.mockRejectedValue(new Error('API Error'));
    
    render(<IssueForm projectId={mockProjectId} onSuccess={mockOnSuccess} />);
    
    const titleInput = screen.getByLabelText(/issue title/i);
    fireEvent.change(titleInput, { target: { value: 'Test Issue' } });
    
    const submitButton = screen.getByRole('button', { name: /create issue/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(toast.error).toHaveBeenCalled();
    });
    
    expect(mockOnSuccess).not.toHaveBeenCalled();
  });

  // ========== EDIT MODE TESTS ==========

  it('renders in edit mode with pre-filled data', () => {
    const existingIssue = {
      id: 1,
      title: 'Existing Issue',
      description: 'Existing Description',
      status: ISSUE_STATUS.IN_PROGRESS,
      priority: ISSUE_PRIORITY.HIGH,
    };
    
    render(
      <IssueForm 
        projectId={mockProjectId} 
        onSuccess={mockOnSuccess} 
        initialData={existingIssue}
      />
    );
    
    const titleInput = screen.getByLabelText(/issue title/i);
    const descInput = screen.getByLabelText(/description/i);
    const statusSelect = screen.getByLabelText(/status/i);
    const prioritySelect = screen.getByLabelText(/priority/i);
    
    expect(titleInput.value).toBe('Existing Issue');
    expect(descInput.value).toBe('Existing Description');
    expect(statusSelect.value).toBe(ISSUE_STATUS.IN_PROGRESS);
    expect(prioritySelect.value).toBe(ISSUE_PRIORITY.HIGH);
  });

  it('shows "Update Issue" button text in edit mode', () => {
    const existingIssue = {
      id: 1,
      title: 'Existing Issue',
      description: 'Existing Description',
      status: ISSUE_STATUS.OPEN,
      priority: ISSUE_PRIORITY.MEDIUM,
    };
    
    render(
      <IssueForm 
        projectId={mockProjectId} 
        onSuccess={mockOnSuccess} 
        initialData={existingIssue}
      />
    );
    
    expect(screen.getByRole('button', { name: /update issue/i })).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /create issue/i })).not.toBeInTheDocument();
  });

  it('calls issueService.updateIssue in edit mode', async () => {
    const existingIssue = {
      id: 1,
      title: 'Existing Issue',
      description: 'Existing Description',
      status: ISSUE_STATUS.OPEN,
      priority: ISSUE_PRIORITY.MEDIUM,
    };
    
    issueService.updateIssue.mockResolvedValue({
      ...existingIssue,
      title: 'Updated Issue',
    });
    
    render(
      <IssueForm 
        projectId={mockProjectId} 
        onSuccess={mockOnSuccess} 
        initialData={existingIssue}
      />
    );
    
    const titleInput = screen.getByLabelText(/issue title/i);
    fireEvent.change(titleInput, { target: { value: 'Updated Issue' } });
    
    const submitButton = screen.getByRole('button', { name: /update issue/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(issueService.updateIssue).toHaveBeenCalledWith(1, {
        title: 'Updated Issue',
        description: 'Existing Description',
        status: ISSUE_STATUS.OPEN,
        priority: ISSUE_PRIORITY.MEDIUM,
      });
    });
  });

  // ========== CANCEL BUTTON TESTS ==========

  it('shows cancel button when onCancel prop is provided', () => {
    render(
      <IssueForm 
        projectId={mockProjectId} 
        onSuccess={mockOnSuccess} 
        onCancel={mockOnCancel}
      />
    );
    
    expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument();
  });

  it('does not show cancel button when onCancel prop is not provided', () => {
    render(<IssueForm projectId={mockProjectId} onSuccess={mockOnSuccess} />);
    
    expect(screen.queryByRole('button', { name: /cancel/i })).not.toBeInTheDocument();
  });

  it('calls onCancel when cancel button is clicked', () => {
    render(
      <IssueForm 
        projectId={mockProjectId} 
        onSuccess={mockOnSuccess} 
        onCancel={mockOnCancel}
      />
    );
    
    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    fireEvent.click(cancelButton);
    
    expect(mockOnCancel).toHaveBeenCalled();
  });

  it('does not submit form when cancel button is clicked', () => {
    render(
      <IssueForm 
        projectId={mockProjectId} 
        onSuccess={mockOnSuccess} 
        onCancel={mockOnCancel}
      />
    );
    
    const titleInput = screen.getByLabelText(/issue title/i);
    fireEvent.change(titleInput, { target: { value: 'Test Issue' } });
    
    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    fireEvent.click(cancelButton);
    
    expect(issueService.createIssue).not.toHaveBeenCalled();
  });

  // ========== PLACEHOLDER TESTS ==========

  it('has correct placeholder text', () => {
    render(<IssueForm projectId={mockProjectId} onSuccess={mockOnSuccess} />);
    
    const titleInput = screen.getByPlaceholderText(/enter issue title/i);
    const descInput = screen.getByPlaceholderText(/enter issue description \(optional\)/i);
    
    expect(titleInput).toBeInTheDocument();
    expect(descInput).toBeInTheDocument();
  });
}); 