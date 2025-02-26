// Helper function to join URL paths
const joinPaths = (...parts: string[]): string => {
  // Filter out empty parts first
  const filteredParts = parts.filter(part => part.trim().length > 0);
  
  // If all parts are empty, return empty string
  if (filteredParts.length === 0) {
    return '';
  }
  
  // Check if the last non-empty part has a trailing slash
  const lastPart = parts.filter(part => part.trim().length > 0).pop() || '';
  const hasTrailingSlash = lastPart.trim().endsWith('/');
  
  // If the first part is empty but the second part starts with a slash, preserve that slash
  if (parts[0].trim() === '' && parts.length > 1 && parts[1].trim().startsWith('/')) {
    const result = parts
      .slice(1)
      .map((part, i) => {
        if (i === 0) {
          // Preserve the leading slash for the first non-empty part when BASENAME is empty
          return part.trim().replace(/[\/]+$/, '');
        } else {
          return part.trim().replace(/(^[\/]+|[\/]+$)/g, '');
        }
      })
      .filter(x => x.length)
      .join('/');
      
    return hasTrailingSlash ? result + '/' : result;
  }
  
  // Original behavior for other cases
  const result = parts
    .map((part, i) => {
      if (i === 0) {
        return part.trim().replace(/[\/]+$/, '');
      } else {
        return part.trim().replace(/(^[\/]+|[\/]+$)/g, '');
      }
    })
    .filter(x => x.length)
    .join('/');
    
  return hasTrailingSlash ? result + '/' : result;
};

export default joinPaths;