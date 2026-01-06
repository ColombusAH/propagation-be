import styled from 'styled-components';
import { useStore } from '@/store';
import { theme } from '@/styles/theme';
import type { Currency } from '@/i18n';

const Container = styled.div`
  display: flex;
  align-items: center;
  gap: ${theme.spacing.xs};
`;

const ToggleButton = styled.button`
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: ${theme.borderRadius.md};
  color: white;
  padding: ${theme.spacing.xs} ${theme.spacing.sm};
  font-size: ${theme.typography.fontSize.sm};
  cursor: pointer;
  transition: all ${theme.transitions.fast};
  display: flex;
  align-items: center;
  gap: 4px;

  &:hover {
    background: rgba(255, 255, 255, 0.3);
  }

  @media (max-width: ${theme.breakpoints.mobile}) {
    padding: ${theme.spacing.xs};
    font-size: ${theme.typography.fontSize.xs};
  }
`;

const CurrencySelect = styled.select`
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: ${theme.borderRadius.md};
  color: white;
  padding: ${theme.spacing.xs} ${theme.spacing.sm};
  font-size: ${theme.typography.fontSize.sm};
  cursor: pointer;
  transition: all ${theme.transitions.fast};

  &:hover {
    background: rgba(255, 255, 255, 0.3);
  }

  option {
    background: ${theme.colors.primary};
    color: white;
  }

  @media (max-width: ${theme.breakpoints.mobile}) {
    padding: ${theme.spacing.xs};
    font-size: ${theme.typography.fontSize.xs};
  }
`;

const Flag = styled.span`
  font-size: 16px;
`;

export function LanguageSwitch() {
    const locale = useStore((state) => state.locale);
    const currency = useStore((state) => state.currency);
    const toggleLocale = useStore((state) => state.toggleLocale);
    const setCurrency = useStore((state) => state.setCurrency);

    const handleCurrencyChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        setCurrency(e.target.value as Currency);
    };

    return (
        <Container>
            <ToggleButton onClick={toggleLocale} aria-label="Toggle language">
                <Flag>{locale === 'he' ? '🇮🇱' : '🇬🇧'}</Flag>
                <span>{locale === 'he' ? 'עב' : 'EN'}</span>
            </ToggleButton>

            <CurrencySelect
                value={currency}
                onChange={handleCurrencyChange}
                aria-label="Select currency"
            >
                <option value="ILS">₪</option>
                <option value="USD">$</option>
                <option value="EUR">€</option>
            </CurrencySelect>
        </Container>
    );
}
