import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { IssueFilters } from '../../src/components/issues/IssueFilters';

describe('IssueFilters', () => {
  it('renders filter dropdowns', () => {
    const mockOnFilterChange = vi.fn();
    const filters = { status: '', priority: '' };
    
    render(<IssueFilters filters={filters} onFilterChange={mockOnFilterChange} />);
    
    expect(screen.getByLabelText(/status/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/priority/i)).toBeInTheDocument();
  });

  it('calls onFilterChange when status changes', () => {
    const mockOnFilterChange = vi.fn();
    const filters = { status: '', priority: '' };
    
    render(<IssueFilters filters={filters} onFilterChange={mockOnFilterChange} />);
    
    const statusSelect = screen.getByLabelText(/status/i);
    fireEvent.change(statusSelect, { target: { value: 'Open' } });
    
    expect(mockOnFilterChange).toHaveBeenCalledWith({ status: 'Open', priority: '' });
  });

  it('calls onFilterChange when priority changes', () => {
    const mockOnFilterChange = vi.fn();
    const filters = { status: '', priority: '' };
    
    render(<IssueFilters filters={filters} onFilterChange={mockOnFilterChange} />);
    
    const prioritySelect = screen.getByLabelText(/priority/i);
    fireEvent.change(prioritySelect, { target: { value: 'High' } });
    
    expect(mockOnFilterChange).toHaveBeenCalledWith({ status: '', priority: 'High' });
  });

  it('shows clear filters button when filters are active', () => {
    const mockOnFilterChange = vi.fn();
    const filters = { status: 'Open', priority: 'High' };
    
    render(<IssueFilters filters={filters} onFilterChange={mockOnFilterChange} />);
    
    expect(screen.getByText(/clear filters/i)).toBeInTheDocument();
  });

  it('clears filters when clear button is clicked', () => {
    const mockOnFilterChange = vi.fn();
    const filters = { status: 'Open', priority: 'High' };
    
    render(<IssueFilters filters={filters} onFilterChange={mockOnFilterChange} />);
    
    const clearButton = screen.getByText(/clear filters/i);
    fireEvent.click(clearButton);
    
    expect(mockOnFilterChange).toHaveBeenCalledWith({ status: '', priority: '' });
  });
});