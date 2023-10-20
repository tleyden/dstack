export const runStatusForDeleting: TJobStatus[] = ['failed', 'stopped', 'aborted', 'done'];
export const runStatusForStopping: TJobStatus[] = ['submitted', 'pending', 'running'];
export const runStatusForAborting: TJobStatus[] = ['submitted', 'pending', 'running', 'stopping', 'restarting'];
export const unfinishedRuns: TJobStatus[] = [
    'building',
    'running',
    'uploading',
    'downloading',
    'stopping',
    'stopped',
    'terminating',
    'pending',
    'restarting',
];
