import { describe, it, expect } from 'vitest';
import { formatCurrency, parseCentsToDecimal } from '../currency';

describe('Currency utilities', () => {
  describe('formatCurrency', () => {
    it('should format cents to USD currency', () => {
      expect(formatCurrency(1000)).toBe('$10.00');
      expect(formatCurrency(100)).toBe('$1.00');
      expect(formatCurrency(99)).toBe('$0.99');
      expect(formatCurrency(1234567)).toBe('$12,345.67');
    });

    it('should handle zero', () => {
      expect(formatCurrency(0)).toBe('$0.00');
    });
  });

  describe('parseCentsToDecimal', () => {
    it('should convert cents to decimal string', () => {
      expect(parseCentsToDecimal(1000)).toBe('10.00');
      expect(parseCentsToDecimal(100)).toBe('1.00');
      expect(parseCentsToDecimal(99)).toBe('0.99');
      expect(parseCentsToDecimal(0)).toBe('0.00');
    });
  });
});

