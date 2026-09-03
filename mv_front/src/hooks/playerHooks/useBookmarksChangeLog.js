import React, { useState, useEffect, useRef } from 'react';
import { v4 as uuidv4 } from 'uuid';

export function useBookmarksChangeLog() {
    const [bookmarksChangeLog, setBookmarksChangeLog] = useState({});

    const manageBookmarksChangeLog = (action, start, end, id = null) => {
        const handlers = {
            CREATE: () => {
                const newId = 'Temp-' + uuidv4();
                return { id: newId, update: { [newId]: { action: 'CREATE', start, end } } };
            },

            UPDATE: () => {
                if (!id) return null;
                
                const currentAction = bookmarksChangeLog[id]?.action;
                if (currentAction === 'DELETE') return null;
                
                return { 
                    id, 
                    update: { [id]: { action: currentAction || 'UPDATE', start, end } } 
                };
            },

            DELETE: () => {
                if (!id) return null;
                
                const currentAction = bookmarksChangeLog[id]?.action;
                
                if (currentAction === 'CREATE') {
                    return { id, delete: true };
                } else if (currentAction !== 'DELETE') {
                    return { id, update: { [id]: { action: 'DELETE' } } };
                }
                
                return null;
            }
        };

        const result = handlers[action]?.();
        if (!result) return;

        setBookmarksChangeLog(prevLog => {
            if (result.delete) {
                const { [result.id]: _, ...updatedLog } = prevLog;
                return updatedLog;
            }
            return { ...prevLog, ...result.update };
        });

        return result.id;
    };

    return { bookmarksChangeLog, setBookmarksChangeLog, manageBookmarksChangeLog };
}