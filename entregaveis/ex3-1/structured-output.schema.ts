import { z } from "zod";

export const structuredOutputSchema = z
	.object({
		answer: z.string().trim().min(1, "answer must not be empty"),
		source_document: z.string().trim().min(1, "source_document must not be empty"),
		confidence_score: z
			.number({ invalid_type_error: "confidence_score must be a number" })
			.min(0, "confidence_score must be between 0 and 1")
			.max(1, "confidence_score must be between 0 and 1"),
	})
	.strict();

export type StructuredOutput = z.infer<typeof structuredOutputSchema>;