import { useState, useEffect, useCallback } from 'react';
import { issueService } from '../api_services/issueService';

export const useIssues = (projectId, filters = {}) => {
  const [issues, setIssues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchIssues = useCallback(async () => {
    if (!projectId) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const data = await issueService.getIssues(projectId, filters);
      setIssues(data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [projectId, filters.status, filters.priority]);

  useEffect(() => {
    fetchIssues();
  }, [fetchIssues]);

  const createIssue = async (issueData) => {
    const newIssue = await issueService.createIssue(projectId, issueData);
    setIssues([newIssue, ...issues]);
    return newIssue;
  };

  const updateIssue = async (issueId, issueData) => {
    const updated = await issueService.updateIssue(issueId, issueData);
    setIssues(issues.map((i) => (i.id === issueId ? updated : i)));
    return updated;
  };

  const deleteIssue = async (issueId) => {
    await issueService.deleteIssue(issueId);
    setIssues(issues.filter((i) => i.id !== issueId));
  };

  return {
    issues,
    loading,
    error,
    fetchIssues,
    createIssue,
    updateIssue,
    deleteIssue,
  };
};