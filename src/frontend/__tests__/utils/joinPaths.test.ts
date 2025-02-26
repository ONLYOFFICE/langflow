import { describe, it, expect } from 'vitest';
import joinPaths from '../../src/utils/joinPaths';

/**
 * Unit tests for the joinPaths utility function
 * 
 * These tests verify that the joinPaths function correctly handles various path joining scenarios,
 * with special attention to preserving leading slashes when needed.
 */
describe('joinPaths utility', () => {
  it('should preserve leading slash when BASENAME is empty', () => {
    // When BASENAME is empty and the path starts with a slash,
    // the leading slash should be preserved
    const result = joinPaths('', '/api/v1/');
    expect(result).toBe('/api/v1/');
  });

  it('should join paths correctly with non-empty first part', () => {
    // When first part doesn't have a trailing slash
    const result1 = joinPaths('base', '/api/v1/');
    expect(result1).toBe('base/api/v1/');

    // When first part has a trailing slash
    const result2 = joinPaths('base/', '/api/v1/');
    expect(result2).toBe('base/api/v1/');
  });

  it('should preserve leading slash when first part starts with slash', () => {
    const result = joinPaths('/base/', '/api/v1/');
    expect(result).toBe('/base/api/v1/');
  });

  it('should handle multiple path parts correctly', () => {
    const result = joinPaths('base', 'api', 'v1', 'endpoint');
    expect(result).toBe('base/api/v1/endpoint');

    const resultWithTrailingSlash = joinPaths('base', 'api', 'v1', 'endpoint/');
    expect(resultWithTrailingSlash).toBe('base/api/v1/endpoint/');
  });

  it('should handle empty parts correctly', () => {
    // Some empty parts
    const result = joinPaths('base', '', 'v1', '');
    expect(result).toBe('base/v1');

    // All empty parts
    const resultAllEmpty = joinPaths('', '', '');
    expect(resultAllEmpty).toBe('');
  });

  it('should trim whitespace from parts', () => {
    const result = joinPaths(' base ', ' /api/v1/ ');
    expect(result).toBe('base/api/v1/');
  });

  it('should handle real-world use cases from the codebase', () => {
    // Test cases based on actual usage in the codebase
    const result1 = joinPaths('', '/api/v1/');
    expect(result1).toBe('/api/v1/');

    const result2 = joinPaths('', '/api/v2/');
    expect(result2).toBe('/api/v2/');

    const result3 = joinPaths('', '/health');
    expect(result3).toBe('/health');

    const result4 = joinPaths('', '/health_check');
    expect(result4).toBe('/health_check');
  });

  it('should handle real-world use cases from the url', () => {
    const result1 = joinPaths('http://localhost:3000', 'virtual', '/api/v1/');
    expect(result1).toBe('http://localhost:3000/virtual/api/v1/');

    const result2 = joinPaths('http://localhost:3000', 'virtual', '/api/v2');
    expect(result2).toBe('http://localhost:3000/virtual/api/v2');
  });

  it('should preserve trailing slash when it exists in the last part', () => {
    // Example 1 from the requirements
    const result1 = joinPaths('', '/api/v2/');
    expect(result1).toBe('/api/v2/');

    // Example 2 from the requirements
    const result2 = joinPaths('', '/health_check');
    expect(result2).toBe('/health_check');

    // Additional test cases
    const result3 = joinPaths('base', 'path/');
    expect(result3).toBe('base/path/');

    const result4 = joinPaths('base/', 'path');
    expect(result4).toBe('base/path');
  });
});
