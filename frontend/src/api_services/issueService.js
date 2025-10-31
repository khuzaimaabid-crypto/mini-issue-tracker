import api from '../api';

export const issueService = {
  async getIssues(projectId, filters = {}) {
    const params = new URLSearchParams();
    if (filters.status) params.append('status', filters.status);
    if (filters.priority) params.append('priority', filters.priority);
    
    const response = await api.get(
      `/projects/${projectId}/issues?${params.toString()}`
    );
    return response.data;
  },

  async getIssue(issueId) {
    const response = await api.get(`/issues/${issueId}`);
    return response.data;
  },

  async createIssue(projectId, issueData) {
    const response = await api.post(`/projects/${projectId}/issues`, issueData);
    return response.data;
  },

  async updateIssue(issueId, issueData) {
    const response = await api.patch(`/issues/${issueId}`, issueData);
    return response.data;
  },

  async deleteIssue(issueId) {
    const response = await api.delete(`/issues/${issueId}`);
    return response.data;
  },
};