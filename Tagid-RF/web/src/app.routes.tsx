import { Routes, Route, Navigate } from 'react-router-dom';
import { DashboardPage } from './pages/DashboardPage';
import { TransactionsPage } from './pages/TransactionsPage';
import { PaymentsPage } from './pages/PaymentsPage';
import { SettingsPage } from './pages/SettingsPage';
import { NotificationsPage } from './pages/NotificationsPage';
import { NotificationSettingsPage } from './pages/NotificationSettingsPage';
import { StoreManagementPage } from './pages/StoreManagementPage';
import { UserManagementPage } from './pages/UserManagementPage';
import { ScanPage } from './pages/ScanPage';
import { CatalogPage } from './pages/CatalogPage';
import { CartPage } from './pages/CartPage';
import { CheckoutPage } from './pages/CheckoutPage';
import { OrderSuccessPage } from './pages/OrderSuccessPage';
import { OrdersPage } from './pages/OrdersPage';
import { QRGeneratorPage } from './pages/QRGeneratorPage';
import { ContainerPage } from './pages/ContainerPage';
import { TagMappingPage } from './pages/TagMappingPage';
import ReaderSettingsPage from './pages/ReaderSettingsPage';
import { StoreBIPage } from './pages/StoreBIPage';
import { TagScannerPage } from './pages/TagScannerPage';
import { TagLinkingPage } from './pages/TagLinkingPage';
import { BathSetupPage } from './pages/BathSetupPage';
import { CustomerCartPage } from './pages/CustomerCartPage';
import { ExitGatePage } from './pages/ExitGatePage.tsx';

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="/dashboard" element={<DashboardPage />} />
      <Route path="/transactions" element={<TransactionsPage />} />
      <Route path="/payments" element={<PaymentsPage />} />
      <Route path="/settings" element={<SettingsPage />} />
      <Route path="/notifications" element={<NotificationsPage />} />
      <Route path="/notification-settings" element={<NotificationSettingsPage />} />
      <Route path="/stores" element={<StoreManagementPage />} />
      <Route path="/users" element={<UserManagementPage />} />
      <Route path="/scan" element={<ScanPage />} />
      <Route path="/catalog" element={<CatalogPage />} />
      <Route path="/cart" element={<CartPage />} />
      <Route path="/checkout" element={<CheckoutPage />} />
      <Route path="/orders" element={<OrdersPage />} />
      <Route path="/orders/:orderId/success" element={<OrderSuccessPage />} />
      <Route path="/qr-generator" element={<QRGeneratorPage />} />
      <Route path="/containers" element={<ContainerPage />} />
      <Route path="/tag-mapping" element={<TagMappingPage />} />
      <Route path="/reader-settings" element={<ReaderSettingsPage />} />
      <Route path="/store-bi" element={<StoreBIPage />} />
      <Route path="/tag-scanner" element={<TagScannerPage />} />
      <Route path="/tag-linking" element={<TagLinkingPage />} />
      <Route path="/bath-setup" element={<BathSetupPage />} />
      <Route path="/customer-cart" element={<CustomerCartPage />} />
      <Route path="/exit-gate" element={<ExitGatePage />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
