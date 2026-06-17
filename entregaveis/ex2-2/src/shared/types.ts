import { z } from "zod";

export const sourceDocumentSchema = z.object({
	title: z.string(),
	url: z.string(),
	vigency: z.string().optional(),
});

export type SourceDocument = z.infer<typeof sourceDocumentSchema>;

export const queryRequestSchema = z.object({
	question: z.string(),
	session_id: z.string().optional(),
});

export type QueryRequest = z.infer<typeof queryRequestSchema>;

export const searchChunkSchema = z.object({
	content: z.string(),
	source_document: sourceDocumentSchema,
	score: z.number(),
});

export type SearchChunk = z.infer<typeof searchChunkSchema>;

export const queryResponseSchema = z.object({
	answer: z.string(),
	sources: z.array(sourceDocumentSchema),
	latency_ms: z.number(),
});

export type QueryResponse = z.infer<typeof queryResponseSchema>;
