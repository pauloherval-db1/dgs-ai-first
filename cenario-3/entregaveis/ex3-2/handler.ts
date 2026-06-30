import { CosmosClient } from '@azure/cosmos';
import { app, HttpRequest, HttpResponseInit } from '@azure/functions';
import pino from 'pino';
import { z } from 'zod';

const feedbackInputSchema = z
  .object({
    queryId: z.string().trim().min(1).max(100),
    rating: z.number().int().min(1).max(5),
    comment: z.string().trim().max(2000).optional().default(''),
    attendantEmail: z.string().trim().email()
  })
  .strict();

type FeedbackInput = z.infer<typeof feedbackInputSchema>;

type FeedbackDocument = FeedbackInput & {
  timestamp: string;
};

const logger = pino({
  name: 'feedback-handler',
  level: process.env.LOG_LEVEL ?? 'info'
});

const cosmosConnectionString = process.env.COSMOS_CONNECTION_STRING;
const cosmosDatabaseName = process.env.COSMOS_DATABASE_NAME ?? 'novatech';
const cosmosContainerName = process.env.COSMOS_FEEDBACK_CONTAINER_NAME ?? 'feedbacks';

const cosmosClient = cosmosConnectionString ? new CosmosClient(cosmosConnectionString) : null;

function jsonResponse(status: number, body: Record<string, unknown>): HttpResponseInit {
  return {
    status,
    headers: {
      'content-type': 'application/json; charset=utf-8'
    },
    jsonBody: body
  };
}

function getFeedbackContainer() {
  if (!cosmosClient) {
    throw new Error('COSMOS_CONNECTION_STRING is not configured');
  }

  return cosmosClient
    .database(cosmosDatabaseName)
    .container(cosmosContainerName);
}

export async function feedbackHandler(request: HttpRequest): Promise<HttpResponseInit> {
  let rawBody: unknown;

  try {
    rawBody = await request.json();
  } catch {
    logger.warn({ route: 'feedback' }, 'Invalid JSON payload for feedback');
    return jsonResponse(400, { error: 'Invalid JSON payload' });
  }

  const parseResult = feedbackInputSchema.safeParse(rawBody);

  if (!parseResult.success) {
    logger.warn(
      {
        route: 'feedback',
        validationIssues: parseResult.error.issues.map((issue) => ({
          path: issue.path.join('.'),
          code: issue.code,
          message: issue.message
        }))
      },
      'Feedback payload validation failed'
    );

    return jsonResponse(400, { error: 'Invalid feedback payload' });
  }

  const parsedFeedback = parseResult.data;

  const feedback: FeedbackDocument = {
    queryId: parsedFeedback.queryId,
    rating: parsedFeedback.rating,
    comment: parsedFeedback.comment,
    attendantEmail: parsedFeedback.attendantEmail,
    timestamp: new Date().toISOString()
  };

  try {
    await getFeedbackContainer().items.create(feedback);

    logger.info(
      {
        route: 'feedback',
        queryId: feedback.queryId,
        rating: feedback.rating
      },
      'Feedback stored successfully'
    );

    return jsonResponse(200, { status: 'ok' });
  } catch (error) {
    logger.error(
      {
        route: 'feedback',
        queryId: feedback.queryId,
        err: error instanceof Error ? error.message : 'Unknown error'
      },
      'Failed to persist feedback'
    );

    return jsonResponse(500, { error: 'Internal server error' });
  }
}

app.http('feedback', {
  methods: ['POST'],
  handler: feedbackHandler
});