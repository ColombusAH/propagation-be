import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export function TagLinkingPage() {
  const navigate = useNavigate();
  useEffect(() => {
    navigate('/tag-mapping');
  }, [navigate]);
  return null;
}
