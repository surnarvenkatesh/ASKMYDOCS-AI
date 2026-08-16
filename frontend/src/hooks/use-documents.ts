import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import type { DocumentListResponse, DocumentRecord } from "@/types/api";

const DOCUMENTS_KEY = ["documents"];

export function useDocuments(search?: string) {
  return useQuery({
    queryKey: [...DOCUMENTS_KEY, search ?? ""],
    queryFn: async () => {
      const { data } = await apiClient.get<DocumentListResponse>("/documents", {
        params: search ? { search } : undefined,
      });
      return data;
    },
  });
}

export function useUploadDocument() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append("file", file);
      const { data } = await apiClient.post<DocumentRecord>("/documents", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: DOCUMENTS_KEY });
    },
  });
}

export function useDeleteDocument() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (documentId: string) => {
      await apiClient.delete(`/documents/${documentId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: DOCUMENTS_KEY });
    },
  });
}

export function useRenameDocument() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ documentId, filename }: { documentId: string; filename: string }) => {
      const { data } = await apiClient.patch<DocumentRecord>(`/documents/${documentId}`, { filename });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: DOCUMENTS_KEY });
    },
  });
}

export function useReindexDocument() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (documentId: string) => {
      const { data } = await apiClient.post<DocumentRecord>(`/documents/${documentId}/reindex`);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: DOCUMENTS_KEY });
    },
  });
}
