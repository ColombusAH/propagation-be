import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { Layout } from '@/components/Layout';
import { formatCurrency } from '@/lib/utils/currency';
import { theme } from '@/styles/theme';
import { fetchOrderById, Order } from '@/api/orders';

const Container = styled.div`
  max-width: 700px;
  margin: 0 auto;
  width: 100%;
  padding: ${theme.spacing.xl};
`;

const SuccessCard = styled.div`
  background: white;
  border-radius: 24px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.05);
  border: 1px solid ${theme.colors.border};
  overflow: hidden;
`;

const TopBanner = styled.div`
  background: #10B981;
  padding: ${theme.spacing.xl} 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  color: white;
`;

const SuccessIcon = styled.div`
  width: 64px;
  height: 64px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: ${theme.spacing.md};
`;

const BannerTitle = styled.h1`
  font-size: 28px;
  font-weight: 800;
  margin: 0;
  letter-spacing: -0.5px;
`;

const Content = styled.div`
  padding: ${theme.spacing.xl};
`;

const Section = styled.div`
  margin-bottom: ${theme.spacing.xl};
`;

const SectionTitle = styled.h2`
  font-size: 14px;
  font-weight: 800;
  text-transform: uppercase;
  color: #64748b;
  letter-spacing: 1px;
  margin-bottom: ${theme.spacing.lg};
  display: flex;
  align-items: center;
  gap: 8px;
`;

const InfoGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: ${theme.spacing.lg};
  background: #F8FAFC;
  padding: ${theme.spacing.lg};
  border-radius: 16px;
`;

const InfoItem = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

const InfoLabel = styled.span`
  font-size: 12px;
  color: #94A3B8;
  font-weight: 600;
`;

const InfoValue = styled.span`
  font-size: 15px;
  color: #1E293B;
  font-weight: 700;
`;

const ItemList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const ItemRow = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 12px;
  border-bottom: 1px solid #F1F5F9;

  &:last-child {
    border-bottom: none;
  }
`;

const ItemInfo = styled.div`
  display: flex;
  flex-direction: column;
`;

const ItemName = styled.span`
  font-size: 16px;
  font-weight: 700;
  color: #1E293B;
`;

const ItemQty = styled.span`
  font-size: 13px;
  color: #64748B;
`;

const ItemPrice = styled.span`
  font-size: 16px;
  font-weight: 800;
  color: #1E293B;
`;

const TotalSection = styled.div`
  margin-top: ${theme.spacing.xl};
  padding: ${theme.spacing.lg};
  background: #1E293B;
  border-radius: 16px;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const TotalLabel = styled.span`
  font-size: 16px;
  font-weight: 600;
  opacity: 0.8;
`;

const TotalAmount = styled.span`
  font-size: 32px;
  font-weight: 800;
`;

const Actions = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: ${theme.spacing.lg};
  margin-top: ${theme.spacing.xl};
`;

const PrimaryButton = styled.button`
  background: #3B82F6;
  color: white;
  border: none;
  padding: 16px;
  border-radius: 12px;
  font-weight: 800;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 16px rgba(59, 130, 246, 0.4);
  }
`;

const SecondaryButton = styled.button`
  background: white;
  color: #1E293B;
  border: 1px solid #E2E8F0;
  padding: 16px;
  border-radius: 12px;
  font-weight: 800;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: #F8FAFC;
    border-color: #CBD5E1;
  }
`;

const MaterialIcon = ({ name, size = 24 }: { name: string; size?: number }) => (
  <span className="material-symbols-outlined" style={{ fontSize: size, display: 'block' }}>{name}</span>
);

export function OrderSuccessPage() {
  const { orderId } = useParams<{ orderId: string }>();
  const navigate = useNavigate();
  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (orderId) {
      fetchOrderById(orderId)
        .then(setOrder)
        .catch(console.error)
        .finally(() => setLoading(false));
    }
  }, [orderId]);

  if (loading) return <Layout><Container>מאמת תשלום...</Container></Layout>;
  if (!order) return <Layout><Container>הזמנה לא נמצאה</Container></Layout>;

  return (
    <Layout>
      <Container>
        <SuccessCard>
          <TopBanner>
            <SuccessIcon>
              <MaterialIcon name="check" size={40} />
            </SuccessIcon>
            <BannerTitle>התשלום בוצע בהצלחה</BannerTitle>
          </TopBanner>

          <Content>
            <Section>
              <SectionTitle>
                <MaterialIcon name="info" size={18} /> פרטי אישור
              </SectionTitle>
              <InfoGrid>
                <InfoItem>
                  <InfoLabel>מספר הזמנה</InfoLabel>
                  <InfoValue>#{order.id.slice(0, 8).toUpperCase()}</InfoValue>
                </InfoItem>
                <InfoItem>
                  <InfoLabel>סטטוס</InfoLabel>
                  <InfoValue style={{ color: '#059669' }}>מאושר</InfoValue>
                </InfoItem>
                <InfoItem>
                  <InfoLabel>תאריך</InfoLabel>
                  <InfoValue>{new Date(order.createdAt).toLocaleDateString('he-IL')}</InfoValue>
                </InfoItem>
                <InfoItem>
                  <InfoLabel>אמצעי תשלום</InfoLabel>
                  <InfoValue>{order.provider}</InfoValue>
                </InfoItem>
              </InfoGrid>
            </Section>

            <Section>
              <SectionTitle>
                <MaterialIcon name="shopping_bag" size={18} /> סיכום רכישה
              </SectionTitle>
              <ItemList>
                {order.items.length > 0 ? order.items.map((item, idx) => (
                  <ItemRow key={idx}>
                    <ItemInfo>
                      <ItemName>{item.productName}</ItemName>
                      <ItemQty>כמות: {item.quantity}</ItemQty>
                    </ItemInfo>
                    <ItemPrice>{formatCurrency(item.priceInCents || 0)}</ItemPrice>
                  </ItemRow>
                )) : (
                  <span style={{ color: '#94A3B8', fontSize: '14px' }}>אין פירוט פריטים זמין</span>
                )}
              </ItemList>
            </Section>

            <TotalSection>
              <TotalLabel>סה"כ לתשלום</TotalLabel>
              <TotalAmount>{formatCurrency(order.totalInCents)}</TotalAmount>
            </TotalSection>
          </Content>
        </SuccessCard>

        <Actions>
          <PrimaryButton onClick={() => navigate('/scan')}>
            התחל רכישה חדשה
          </PrimaryButton>
          <SecondaryButton onClick={() => navigate('/orders')}>
            היסטוריית הזמנות
          </SecondaryButton>
        </Actions>
      </Container>
    </Layout>
  );
}
