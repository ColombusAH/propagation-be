import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QuantityInput } from '../QuantityInput';

describe('QuantityInput', () => {
  it('should render with initial value', () => {
    render(<QuantityInput value={5} onChange={() => { }} />);

    const input = screen.getByRole('spinbutton');
    expect(input).toHaveValue(5);
  });

  it('should increment value when + button is clicked', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();

    render(<QuantityInput value={5} onChange={onChange} />);

    const incrementButton = screen.getByText('+');
    await user.click(incrementButton);

    expect(onChange).toHaveBeenCalledWith(6);
  });

  it('should decrement value when - button is clicked', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();

    render(<QuantityInput value={5} onChange={onChange} />);

    const decrementButton = screen.getByText('−');
    await user.click(decrementButton);

    expect(onChange).toHaveBeenCalledWith(4);
  });

  it('should disable decrement button at minimum', () => {
    render(<QuantityInput value={1} onChange={() => { }} min={1} />);

    const decrementButton = screen.getByText('−');
    expect(decrementButton).toBeDisabled();
  });

  it('should disable increment button at maximum', () => {
    render(<QuantityInput value={10} onChange={() => { }} max={10} />);

    const incrementButton = screen.getByText('+');
    expect(incrementButton).toBeDisabled();
  });

  it.skip('should handle direct input', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();

    render(<QuantityInput value={5} onChange={onChange} />);

    const input = screen.getByRole('spinbutton');
    await user.clear(input);
    await user.type(input, '10');

    expect(onChange).toHaveBeenLastCalledWith(10);
  });
});

