import { Injectable, NgZone } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, Subject } from 'rxjs';
import { environment } from '../environments/environment';

export interface ChatMessage {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    citations?: Citation[];
    isStreaming?: boolean;
}

export interface Citation {
    id: string;
    title: string;
    score: number;
}

@Injectable({
    providedIn: 'root'
})
export class ChatService {
    private apiUrl = environment.apiUrl;

    constructor(private http: HttpClient, private zone: NgZone) { }

    sendMessageStream(query: string, sessionId: string): Observable<any> {
        return new Observable(observer => {
            const url = `${this.apiUrl}/chat/stream?q=${encodeURIComponent(query)}&sessionId=${sessionId}`;
            const eventSource = new EventSource(url);

            eventSource.onmessage = (event) => {
                // This usually catches messages without event type, but we use named events
            };

            eventSource.addEventListener('meta', (event: any) => {
                this.zone.run(() => observer.next({ type: 'meta', data: JSON.parse(event.data) }));
            });

            eventSource.addEventListener('token', (event: any) => {
                this.zone.run(() => observer.next({ type: 'token', data: JSON.parse(event.data) }));
            });

            eventSource.addEventListener('done', (event: any) => {
                this.zone.run(() => {
                    observer.next({ type: 'done', data: JSON.parse(event.data) });
                    observer.complete();
                    eventSource.close();
                });
            });

            eventSource.onerror = (error) => {
                this.zone.run(() => {
                    observer.error(error);
                    eventSource.close();
                });
            };

            return () => eventSource.close();
        });
    }
}
