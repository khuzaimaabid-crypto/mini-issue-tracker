export const ISSUE_STATUS = {
  OPEN: 'Open',
  IN_PROGRESS: 'In Progress',
  CLOSED: 'Closed',
};

export const ISSUE_PRIORITY = {
  LOW: 'Low',
  MEDIUM: 'Medium',
  HIGH: 'High',
};

export const STATUS_COLORS = {
  [ISSUE_STATUS.OPEN]: 'bg-blue-100 text-blue-800',
  [ISSUE_STATUS.IN_PROGRESS]: 'bg-yellow-100 text-yellow-800',
  [ISSUE_STATUS.CLOSED]: 'bg-green-100 text-green-800',
};

export const PRIORITY_COLORS = {
  [ISSUE_PRIORITY.LOW]: 'bg-gray-100 text-gray-800',
  [ISSUE_PRIORITY.MEDIUM]: 'bg-orange-100 text-orange-800',
  [ISSUE_PRIORITY.HIGH]: 'bg-red-100 text-red-800',
};

export const VALIDATION = {
  EMAIL_REGEX: /\S+@\S+\.\S+/,
  MIN_PASSWORD_LENGTH: 6,
  MIN_NAME_LENGTH: 2,
};