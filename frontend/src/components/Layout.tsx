import { Link, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

function Layout() {
  const { isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="app-shell">
      <header className="header">
        <div className="brand">
          <Link to="/">Team Task Tracker</Link>
        </div>

        <nav className="nav-links">
          <Link to="/tasks">Tasks</Link>
          {isAuthenticated ? (
            <button className="logout-button" onClick={handleLogout}>
              Logout
            </button>
          ) : (
            <Link to="/login">Login</Link>
          )}
        </nav>
      </header>

      <section className="content">
        <Outlet />
      </section>
    </div>
  );
}

export default Layout;
