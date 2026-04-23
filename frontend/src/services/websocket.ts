import { useEffect, useRef, useState } from 'react';

export interface WSMessage {
  type: string;
  data: any;
  timestamp: string;
}

type MessageHandler = (message: WSMessage) => void;

const API_BASE_URL = (import.meta.env.VITE_API_URL || '/api/v1').replace(/\/$/, '');

const resolveWebSocketUrl = (customUrl?: string) => {
  if (customUrl) {
    return customUrl;
  }

  // If API base is absolute (e.g., https://api.smart-heaven.com/api/v1)
  if (/^https?:\/\//i.test(API_BASE_URL)) {
    return `${API_BASE_URL.replace(/^http/i, 'ws')}/ws`;
  }

  // Relative API base (local/dev via same host/proxy)
  const wsProtocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
  return `${wsProtocol}://${window.location.host}${API_BASE_URL}/ws`;
};

export const useWebSocket = (url?: string) => {
  const wsUrl = resolveWebSocketUrl(url);
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WSMessage | null>(null);
  const ws = useRef<WebSocket | null>(null);
  const handlers = useRef<Map<string, MessageHandler[]>>(new Map());

  useEffect(() => {
    let reconnectTimer: ReturnType<typeof setTimeout> | null = null;

    const connect = () => {
      try {
        ws.current = new WebSocket(wsUrl);
      } catch (error) {
        console.error('WebSocket initialization error:', error);
        setIsConnected(false);
        reconnectTimer = setTimeout(connect, 3000);
        return;
      }

      ws.current.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
      };

      ws.current.onmessage = (event) => {
        try {
          const message: WSMessage = JSON.parse(event.data);
          setLastMessage(message);

          // Call registered handlers for this message type
          const typeHandlers = handlers.current.get(message.type) || [];
          typeHandlers.forEach(handler => handler(message));

          // Call wildcard handlers
          const wildcardHandlers = handlers.current.get('*') || [];
          wildcardHandlers.forEach(handler => handler(message));
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      ws.current.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        
        // Reconnect after 3 seconds
        reconnectTimer = setTimeout(connect, 3000);
      };
    };

    connect();

    return () => {
      if (reconnectTimer) {
        clearTimeout(reconnectTimer);
      }
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [wsUrl]);

  const send = (data: any) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(data));
    } else {
      console.warn('WebSocket is not connected');
    }
  };

  const subscribe = (messageType: string, handler: MessageHandler) => {
    const typeHandlers = handlers.current.get(messageType) || [];
    typeHandlers.push(handler);
    handlers.current.set(messageType, typeHandlers);

    // Return unsubscribe function
    return () => {
      const currentHandlers = handlers.current.get(messageType) || [];
      const index = currentHandlers.indexOf(handler);
      if (index > -1) {
        currentHandlers.splice(index, 1);
        handlers.current.set(messageType, currentHandlers);
      }
    };
  };

  return {
    isConnected,
    lastMessage,
    send,
    subscribe,
  };
};
