import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { EmptyState } from '../EmptyState';

describe('EmptyState', () => {
  it('should render title and message', () => {
    render(<EmptyState title="Test Title" message="Test Message" />);

    expect(screen.getByText('Test Title')).toBeInTheDocument();
    expect(screen.getByText('Test Message')).toBeInTheDocument();
  });

  it('should render icon when provided', () => {
    render(<EmptyState icon="🎉" title="Test" />);

    expect(screen.getByText('🎉')).toBeInTheDocument();
  });

  it('should render action when provided', () => {
    render(
      <EmptyState
        title="Test"
        action={<button>Click me</button>}
      />
    );

    expect(screen.getByRole('button', { name: 'Click me' })).toBeInTheDocument();
  });

  it('should not render message when not provided', () => {
    const { container } = render(<EmptyState title="Test" />);

    const paragraphs = container.querySelectorAll('p');
    expect(paragraphs.length).toBe(0);
  });
});

