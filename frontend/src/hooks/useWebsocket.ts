import { useEffect, useRef } from 'react';

interface WebsocketOptions {
  userId: number | null;
  onMessage: (event: MessageEvent) => void;
}

function buildWebsocketUrl(userId: number | null): string {
  if (!userId) {
    return '';
  }

  const apiBase = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api';
  const url = new URL(apiBase);
  const protocol = url.protocol === 'https:' ? 'wss:' : 'ws:';
  return `${protocol}//${url.host}/ws/${userId}`;
}

function useWebsocket({ userId, onMessage }: WebsocketOptions) {
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!userId) {
      return;
    }

    const wsUrl = buildWebsocketUrl(userId);
    const socket = new WebSocket(wsUrl);
    socketRef.current = socket;

    socket.addEventListener('message', onMessage);
    socket.addEventListener('error', () => {
      console.warn('WebSocket connection error');
    });

    return () => {
      socket.removeEventListener('message', onMessage);
      socket.close();
      socketRef.current = null;
    };
  }, [userId, onMessage]);
}

export default useWebsocket;
