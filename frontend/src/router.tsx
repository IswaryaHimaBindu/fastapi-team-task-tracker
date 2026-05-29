import { createBrowserRouter, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Login from './pages/Login';
import Tasks from './pages/Tasks';
import { useAuth } from './contexts/AuthContext';

function PrivateRoute({ children }: { children: JSX.Element }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/login" replace />;
}

const router = createBrowserRouter([
  {
    element: <Layout />,
    children: [
      { path: '/login', element: <Login /> },
      { path: '/tasks', element: <PrivateRoute><Tasks /></PrivateRoute> },
      { path: '/', element: <Navigate to="/tasks" replace /> },
    ],
  },
]);

export default router;
