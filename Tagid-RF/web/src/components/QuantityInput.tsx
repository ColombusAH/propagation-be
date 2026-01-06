import styled from 'styled-components';
import { theme } from '@/styles/theme';

interface QuantityInputProps {
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
}

const Container = styled.div`
  display: flex;
  align-items: center;
  gap: ${theme.spacing.sm};
`;

const Button = styled.button`
  background-color: ${theme.colors.backgroundAlt};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.md};
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-weight: ${theme.typography.fontWeight.bold};
  transition: all ${theme.transitions.fast};

  &:hover:not(:disabled) {
    background-color: ${theme.colors.border};
    border-color: ${theme.colors.borderDark};
  }

  &:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }

  &:active:not(:disabled) {
    transform: scale(0.95);
  }
`;

const Input = styled.input`
  width: 50px;
  height: 32px;
  text-align: center;
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.md};
  font-size: ${theme.typography.fontSize.base};
  font-weight: ${theme.typography.fontWeight.medium};

  &:focus {
    outline: none;
    border-color: ${theme.colors.primary};
  }

  /* Remove spinner arrows */
  &::-webkit-inner-spin-button,
  &::-webkit-outer-spin-button {
    -webkit-appearance: none;
    margin: 0;
  }
  -moz-appearance: textfield;
`;

export function QuantityInput({
  value,
  onChange,
  min = 1,
  max = 99,
}: QuantityInputProps) {
  const handleDecrement = () => {
    if (value > min) {
      onChange(value - 1);
    }
  };

  const handleIncrement = () => {
    if (value < max) {
      onChange(value + 1);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = parseInt(e.target.value, 10);
    if (!isNaN(newValue) && newValue >= min && newValue <= max) {
      onChange(newValue);
    }
  };

  return (
    <Container>
      <Button onClick={handleDecrement} disabled={value <= min}>
        −
      </Button>
      <Input
        type="number"
        value={value}
        onChange={handleInputChange}
        min={min}
        max={max}
      />
      <Button onClick={handleIncrement} disabled={value >= max}>
        +
      </Button>
    </Container>
  );
}

