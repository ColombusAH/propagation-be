import { Routes, Route, Navigate } from 'react-router-dom';
import { DashboardPage } from './pages/DashboardPage';
import { TransactionsPage } from './pages/TransactionsPage';
import { SettingsPage } from './pages/SettingsPage';
import { ScanPage } from './pages/ScanPage';
import { CatalogPage } from './pages/CatalogPage';
import { CartPage } from './pages/CartPage';
import { CheckoutPage } from './pages/CheckoutPage';
import { OrderSuccessPage } from './pages/OrderSuccessPage';
import { OrdersPage } from './pages/OrdersPage';
import { QRGeneratorPage } from './pages/QRGeneratorPage';
import { ContainerPage } from './pages/ContainerPage';
import { TagMappingPage } from './pages/TagMappingPage';

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="/dashboard" element={<DashboardPage />} />
      <Route path="/transactions" element={<TransactionsPage />} />
      <Route path="/settings" element={<SettingsPage />} />
      <Route path="/scan" element={<ScanPage />} />
      <Route path="/catalog" element={<CatalogPage />} />
      <Route path="/cart" element={<CartPage />} />
      <Route path="/checkout" element={<CheckoutPage />} />
      <Route path="/orders" element={<OrdersPage />} />
      <Route path="/orders/:orderId/success" element={<OrderSuccessPage />} />
      <Route path="/qr-generator" element={<QRGeneratorPage />} />
      <Route path="/containers" element={<ContainerPage />} />
      <Route path="/tag-mapping" element={<TagMappingPage />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
