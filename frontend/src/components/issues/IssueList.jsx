import { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { issueService } from '../../api_services/issueService';
import { IssueCard } from './IssueCard';
import { IssueForm } from './IssueForm';
import { IssueFilters } from './IssueFilters';
import { Button } from '../app-ui/Button';
import { LoadingSpinner } from '../app-ui/LoadingSpinner';
import toast from 'react-hot-toast';

export const IssueList = () => {
  const { projectId } = useParams();
  const [issues, setIssues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [filters, setFilters] = useState({ status: '', priority: '' });
  const [editingIssue, setEditingIssue] = useState(null);

  const loadIssues = useCallback(async () => {
    try {
      const filterParams = {};
      if (filters.status) filterParams.status = filters.status;
      if (filters.priority) filterParams.priority = filters.priority;

      const data = await issueService.getIssues(projectId, filterParams);
      setIssues(data);
    } catch (error) {
      toast.error('Failed to load issues');
    } finally {
      setLoading(false);
    }
  }, [projectId, filters.status, filters.priority]);

  useEffect(() => {
    loadIssues();
  }, [loadIssues]);

  const handleIssueCreated = (newIssue) => {
    setIssues([newIssue, ...issues]);
    setShowForm(false);
    toast.success('Issue created successfully');
  };

  const handleIssueUpdated = (updatedIssue) => {
    setIssues(issues.map((issue) =>
      issue.id === updatedIssue.id ? updatedIssue : issue
    ));
    setEditingIssue(null);
    toast.success('Issue updated successfully');
  };

  const handleDeleteIssue = async (issueId) => {
    if (!window.confirm('Are you sure you want to delete this issue?')) {
      return;
    }

    try {
      await issueService.deleteIssue(issueId);
      setIssues(issues.filter((i) => i.id !== issueId));
      toast.success('Issue deleted successfully');
    } catch (error) {
      toast.error('Failed to delete issue');
    }
  };

  if (loading) {
    return <LoadingSpinner variant="section" />;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Issues</h2>
        <Button onClick={() => {
          setShowForm(!showForm);
          setEditingIssue(null);
        }}>
          {showForm ? 'Cancel' : 'New Issue'}
        </Button>
      </div>

      <IssueFilters filters={filters} onFilterChange={setFilters} />

      {showForm && (
        <div className="bg-white p-6 rounded-lg shadow">
          <IssueForm projectId={projectId} onSuccess={handleIssueCreated} />
        </div>
      )}

      {issues.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">No issues found. Create your first issue!</p>
        </div>
      ) : (
        <div className="space-y-4">
          {issues.map((issue) => (
            <IssueCard
              key={issue.id}
              issue={issue}
              onEdit={setEditingIssue}
              onDelete={handleDeleteIssue}
              onUpdate={handleIssueUpdated}
              isEditing={editingIssue?.id === issue.id}
            />
          ))}
        </div>
      )}
    </div>
  );
};