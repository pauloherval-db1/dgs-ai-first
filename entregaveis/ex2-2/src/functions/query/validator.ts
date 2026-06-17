import { ZodError, ZodIssueCode, z } from "zod";

import { queryValidationMessages } from "../../shared/messages";
import { queryRequestSchema, type QueryRequest } from "../../shared/types";

export const queryValidatorSchema = queryRequestSchema.extend({
	question: z
		.string()
		.trim()
		.min(1, queryValidationMessages.questionEmpty)
		.max(1000, queryValidationMessages.questionMaxLength),
});

export function validateQueryRequest(input: unknown): QueryRequest {
	try {
		return queryValidatorSchema.parse(input);
	} catch (error) {
		if (error instanceof ZodError) {
			throw new Error(formatQueryValidationMessage(error));
		}

		throw error;
	}
}

function formatQueryValidationMessage(error: ZodError): string {
	const questionIssue = error.issues.find((issue) => issue.path.join(".") === "question");

	if (questionIssue?.code === ZodIssueCode.too_small) {
		return queryValidationMessages.questionEmpty;
	}

	if (questionIssue?.code === ZodIssueCode.too_big) {
		return queryValidationMessages.questionMaxLength;
	}

	return error.issues
		.map((issue) => {
			const path = issue.path.length > 0 ? issue.path.join(".") : "input";

			if (issue.code === ZodIssueCode.invalid_type && issue.expected === "string") {
				if (path === "question") {
					return queryValidationMessages.questionMustBeString;
				}

				return `${path} must be a string`;
			}

			return `${path}: ${issue.message}`;
		})
		.join("; ");
}
