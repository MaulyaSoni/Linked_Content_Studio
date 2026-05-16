
export function formatError(error: any): string {
  if (typeof error === 'string') return error;
  
  if (error?.response?.data?.detail) {
    const detail = error.response.data.detail;
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) {
      return detail.map((d: any) => d.msg || JSON.stringify(d)).join(', ');
    }
    if (typeof detail === 'object') {
      return detail.msg || JSON.stringify(detail);
    }
  }
  
  return error?.message || 'An unexpected error occurred';
}
