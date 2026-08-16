export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export type DocumentStatus = "pending" | "processing" | "indexed" | "failed";
export type DocumentType = "pdf" | "docx" | "txt" | "markdown";

export interface DocumentRecord {
  id: string;
  filename: string;
  file_type: DocumentType;
  file_size_bytes: number;
  status: DocumentStatus;
  error_message: string | null;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface DocumentListResponse {
  documents: DocumentRecord[];
  total: number;
}

export interface Citation {
  ref_id: number;
  document_filename: string;
  page_number: number | null;
  chunk_id: string;
  confidence_score: number;
  snippet: string;
}

export type MessageRole = "user" | "assistant";

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  citations: Citation[];
  generation_metadata: Record<string, unknown>;
  created_at: string;
}

export interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface ConversationDetail extends Conversation {
  messages: ChatMessage[];
}

export type StreamEventType = "token" | "citations" | "warning" | "error" | "done";

export interface StreamEvent {
  type: StreamEventType;
  text: string;
  citations: Citation[];
  metadata: Record<string, unknown>;
}
