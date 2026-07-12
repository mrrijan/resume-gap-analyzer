<?php

namespace App\Services;

use Illuminate\Http\Client\ConnectionException;
use Illuminate\Http\Client\PendingRequest;
use Illuminate\Http\Client\RequestException;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

/**
 * Single point of integration with the FastAPI ML service.
 *
 * All Laravel controllers that need parsing, matching, or gap analysis go
 * through this class. Never call Http::post() to FastAPI from a controller
 * directly — centralizing here means:
 *   - base URL / timeout config in one place
 *   - consistent error handling and logging
 *   - retries/circuit-breaking easy to add later
 *   - easily mockable in tests
 */
class FastApiClient
{
    private string $baseUrl;
    private int $timeout;

    public function __construct()
    {
        $this->baseUrl = config('services.fastapi.base_url');
        $this->timeout = (int) config('services.fastapi.timeout');
    }

    // ---------- M1: Resume parsing ----------
    public function parseResume(string $fileContents, string $filename): array
    {
        try {
            $response = $this->client()
                ->attach('file', $fileContents, $filename)
                ->post('/parse-resume');

            $response->throw();

            return $response->json();
        } catch (RequestException|ConnectionException $e) {
            $this->logAndThrow('parse-resume', $e);
        }
    }

    // ---------- M2: Posting parsing ----------
    public function parsePosting(string $text): array
    {
        return $this->postJson('/parse-posting', ['text' => $text]);
    }

    // ---------- M3: Matching ----------
    public function match(array $payload): array
    {
        return $this->postJson('/match', $payload);
    }

    // ---------- M4: Gap analysis ----------
    public function gapAnalysis(array $postingMatches): array
    {
        return $this->postJson('/gap-analysis', [
            'posting_matches' => $postingMatches,
        ]);
    }

    // ---------- Internals ----------
    private function client(): PendingRequest
    {
        return Http::baseUrl($this->baseUrl)
            ->timeout($this->timeout)
            ->acceptJson();
    }

    private function postJson(string $path, array $payload): array
    {
        try {
            $response = $this->client()
                ->asJson()
                ->post($path, $payload);

            $response->throw();

            return $response->json();
        } catch (RequestException|ConnectionException $e) {
            $this->logAndThrow($path, $e);
        }
    }

    private function logAndThrow(string $endpoint, \Throwable $e): never
    {
        Log::error("FastAPI call failed: {$endpoint}", [
            'error' => $e->getMessage(),
            'endpoint' => $endpoint,
        ]);

        throw new FastApiException(
            "ML service call to {$endpoint} failed: {$e->getMessage()}",
            previous: $e,
        );
    }
}
