// Deterministic guardrails — these checks always run after the model responds,
// regardless of what the prompt requested. The prompt asks for the correct format
// probabilistically; this module enforces it deterministically.
import {
	structuredOutputSchema,
	type StructuredOutput,
} from "./structured-output.schema";

const guardrailMessage =
	"Não foi possível responder com segurança com base na documentação oficial. Encaminhe para revisão humana.";

// "missing_source_document" was removed: the schema already enforces
// source_document presence via .trim().min(1), so that path was dead code.
// Schema failures are reported uniformly as "schema_validation_failed".
export type RejectionReason =
	| "schema_validation_failed"
	| "dangerous_cargo_return_without_negative";

// Structured metadata about why a response was rejected.
// Never includes answer content — only pattern group names and schema paths.
export interface RejectionDetail {
	guardrailId: "schema_validation" | "dangerous_cargo_return";
	triggeredPatterns?: string[];  // logical names of what matched (not content)
	schemaFieldErrors?: string[];  // Zod field paths that failed (e.g. ["source_document"])
}

export interface ValidationResult {
	accepted: boolean;
	reason?: RejectionReason;
	response: StructuredOutput;
	rejectionDetail?: RejectionDetail;
}

export type ValidatorLogger = (reason: RejectionReason, detail: RejectionDetail) => void;

export const safeFallbackResponse: StructuredOutput = {
	answer: guardrailMessage,
	source_document: "SYSTEM-GUARDRAIL",
	confidence_score: 0,
};

export function validateAssistantResponse(
	rawResponse: unknown,
	logger: ValidatorLogger = () => undefined,
): ValidationResult {
	const parsed = structuredOutputSchema.safeParse(rawResponse);

	if (!parsed.success) {
		const schemaFieldErrors = parsed.error.issues.map((issue) =>
			issue.path.join(".") || issue.message,
		);
		const detail: RejectionDetail = {
			guardrailId: "schema_validation",
			schemaFieldErrors,
		};
		logger("schema_validation_failed", detail);

		return {
			accepted: false,
			reason: "schema_validation_failed",
			response: safeFallbackResponse,
			rejectionDetail: detail,
		};
	}

	const response = parsed.data;
	const cargoCheck = checkDangerousCargoReturnGuardrail(response.answer);

	if (cargoCheck.violated) {
		const detail: RejectionDetail = {
			guardrailId: "dangerous_cargo_return",
			triggeredPatterns: cargoCheck.triggeredPatterns,
		};
		logger("dangerous_cargo_return_without_negative", detail);

		return {
			accepted: false,
			reason: "dangerous_cargo_return_without_negative",
			response: safeFallbackResponse,
			rejectionDetail: detail,
		};
	}

	return {
		accepted: true,
		response,
	};
}

interface CargoGuardrailResult {
	violated: boolean;
	triggeredPatterns: string[];
}

function checkDangerousCargoReturnGuardrail(answer: string): CargoGuardrailResult {
	const normalized = normalize(answer);
	const triggeredPatterns: string[] = [];

	// Expanded to cover synonyms and ANTT class references, not just the literal phrase.
	const mentionsDangerousCargo =
		/\bcargas?\s+perigosas?\b/.test(normalized) ||
		/\bprodutos?\s+perigosos?\b/.test(normalized) ||
		/\bmercadorias?\s+perigosas?\b/.test(normalized) ||
		/\bmateriais?\s+perigosos?\b/.test(normalized) ||
		/\bclasses?\s+\d.*\bantt\b/.test(normalized);

	if (mentionsDangerousCargo) triggeredPatterns.push("dangerous_cargo_mention");

	// Expanded to cover "retorno" and "reenvio", common logistics synonyms for devolução.
	const mentionsReturn =
		/\bdevoluc(?:ao|oes)\b|\bdevolver\b|\bdevolvid[oa]s?\b/.test(normalized) ||
		/\bretorno\b/.test(normalized) ||
		/\breenvio\b/.test(normalized);

	if (mentionsReturn) triggeredPatterns.push("return_mention");

	if (!mentionsDangerousCargo || !mentionsReturn) {
		return { violated: false, triggeredPatterns };
	}

	// Expanded to cover negatives beyond "não pode/podem" and "não é possível".
	const hasNegativeSignal =
		/\bnao\s+pod(?:e|em)\b/.test(normalized) ||
		/\bnao\s+e\s+possivel\b/.test(normalized) ||
		/\bnao\s+sao\s+elegiveis\b/.test(normalized) ||
		/\bnao\s+e\s+permitid[oa]s?\b/.test(normalized) ||
		/\bnao\s+se\s+aplica\b/.test(normalized) ||
		/\bimpossivel\b/.test(normalized) ||
		/\bproibid[oa]s?\b/.test(normalized) ||
		/\bvedad[oa]s?\b/.test(normalized) ||
		/\bineligiveis?\b/.test(normalized) ||
		/\bexcluidos?\b/.test(normalized);

	if (!hasNegativeSignal) triggeredPatterns.push("no_negative_signal");

	return { violated: !hasNegativeSignal, triggeredPatterns };
}

function normalize(text: string): string {
	return text
		.normalize("NFD")
		.replace(/[\u0300-\u036f]/g, "")
		.toLowerCase();
}
