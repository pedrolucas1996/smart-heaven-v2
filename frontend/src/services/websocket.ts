import { useEffect, useRef, useState } from 'react';

export interface WSMessage {
  type: string;
  data: any;
  timestamp: string;
}

type MessageHandler = (message: WSMessage) => void;

export const useWebSocket = (url: string = 'ws://localhost:8000/api/v1/ws') => {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WSMessage | null>(null);
  const ws = useRef<WebSocket | null>(null);
  const handlers = useRef<Map<string, MessageHandler[]>>(new Map());

  useEffect(() => {
    const connect = () => {
      ws.current = new WebSocket(url);

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
        setTimeout(connect, 3000);
      };
    };

    connect();

    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [url]);

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
