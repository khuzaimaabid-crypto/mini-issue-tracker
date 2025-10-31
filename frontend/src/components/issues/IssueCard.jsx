import { useState } from 'react';
import { IssueForm } from './IssueForm';
import { Button } from '../app-ui/Button';
import { STATUS_COLORS, PRIORITY_COLORS } from '../../utils/constants';
import { DateHelper } from '../../helpers/dateHelper';

export const IssueCard = ({ issue, onEdit, onDelete, onUpdate, isEditing }) => {
  // Early return for invalid data
  if (!issue || !issue.id) {
    return null;
  }

  // ...existing code...

  if (isEditing) {
    return (
      <div className="bg-white p-6 rounded-lg shadow">
        <IssueForm
          projectId={issue.project_id}
          initialData={issue}
          onSuccess={onUpdate}
          onCancel={() => onEdit && onEdit(null)}  // Check onEdit exists(Safeguard)
        />
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow hover:shadow-md transition-shadow duration-200 p-6">
      <div className="flex items-start justify-between">
        <div className="flex-1">
           <h3 className="text-lg font-semibold text-gray-900 mb-2">
            {issue.title || 'Untitled Issue'} 
          </h3>
          {issue.description && (
            <p className="text-gray-600 text-sm mb-4">{issue.description}</p>
          )}
          
          <div className="flex items-center space-x-3 mb-3">
            <span className={`px-2 py-1 text-xs font-semibold rounded-full ${ STATUS_COLORS[issue.status] || 'bg-gray-100 text-gray-800'}`}>
             {issue.status || 'Unknown'}
            </span>
            <span className={`px-2 py-1 text-xs font-semibold rounded-full ${PRIORITY_COLORS[issue.priority] || 'bg-gray-100 text-gray-800'}`}>
              {issue.priority || 'Unknown'}
            </span>
          </div>
          
          <div className="text-xs text-gray-500">
            Created {DateHelper.formatDate(issue.created_at)} • Updated {DateHelper.formatDate(issue.updated_at)}
          </div>
        </div>
        
        <div className="flex space-x-2 ml-4">
          <Button
            onClick={() => onEdit && onEdit(issue)}
            variant="outline_primary"
            size="xs"
          >
            Edit
          </Button>
          <Button
            onClick={() => onDelete && onDelete(issue.id)}
            variant="outline_danger"
            size="xs"
          >
            Delete
          </Button>
        </div>
      </div>
    </div>
  );
};