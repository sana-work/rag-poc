import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChatService, ChatMessage } from './chat.service';
import { v4 as uuidv4 } from 'uuid';

@Component({
    selector: 'app-root',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.css']
})
export class AppComponent {
    messages: ChatMessage[] = [];
    inputMessage: string = '';
    isLoading: boolean = false;
    sessionId: string = uuidv4();

    constructor(private chatService: ChatService) { }

    sendMessage() {
        if (!this.inputMessage.trim()) return;

        const userMsg: ChatMessage = {
            id: uuidv4(),
            role: 'user',
            content: this.inputMessage
        };
        this.messages.push(userMsg);

        const assistantMsg: ChatMessage = {
            id: uuidv4(),
            role: 'assistant',
            content: '',
            isStreaming: true
        };
        this.messages.push(assistantMsg);

        const query = this.inputMessage;
        this.inputMessage = '';
        this.isLoading = true;

        this.chatService.sendMessageStream(query, this.sessionId).subscribe({
            next: (event) => {
                if (event.type === 'meta') {
                    assistantMsg.citations = event.data.citations;
                } else if (event.type === 'token') {
                    assistantMsg.content += event.data.text;
                } else if (event.type === 'done') {
                    assistantMsg.isStreaming = false;
                    this.isLoading = false;
                }
            },
            error: (err) => {
                console.error('Stream error', err);
                assistantMsg.content += '\n[Error: Connection failed]';
                assistantMsg.isStreaming = false;
                this.isLoading = false;
            }
        });
    }
}
