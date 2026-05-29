interface NotificationItem {
  id: string;
  title: string;
  message: string;
}

interface NotificationsProps {
  notifications: NotificationItem[];
}

function Notifications({ notifications }: NotificationsProps) {
  return (
    <div className="notifications-panel">
      {notifications.map((notification) => (
        <div key={notification.id} className="notification-card">
          <strong>{notification.title}</strong>
          <p>{notification.message}</p>
        </div>
      ))}
    </div>
  );
}

export type { NotificationItem };
export default Notifications;
