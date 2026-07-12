<?php

namespace App\Http\Controllers;

use App\Http\Requests\PostingStoreRequest;
use App\Http\Resources\PostingResource;
use App\Models\Posting;
use App\Services\FastApiClient;
use App\Services\FastApiException;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Http\Response;

class PostingController extends Controller
{
    public function __construct(private FastApiClient $fastApi) {}

    /**
     * List all postings belonging to the authenticated user.
     */
    public function index(Request $request): JsonResponse
    {
        $postings = Posting::query()
            ->where('user_id', $request->user()->id)
            ->orderByDesc('created_at')
            ->get();

        return response()->json([
            'postings' => PostingResource::collection($postings),
        ]);
    }

    /**
     * Parse a pasted job posting text via FastAPI and store it.
     */
    public function store(PostingStoreRequest $request): JsonResponse
    {
        try {
            $parsed = $this->fastApi->parsePosting($request->string('text'));
        } catch (FastApiException $e) {
            return response()->json([
                'message' => 'Failed to parse job posting. Please try again.',
            ], Response::HTTP_BAD_GATEWAY);
        }

        $posting = Posting::create([
            'user_id'    => $request->user()->id,
            'title'      => $request->input('title') ?: $this->deriveTitle($request->string('text')),
            'raw_text'   => $request->string('text'),
            'parsed_json'=> $parsed,
            'source_url' => $request->input('source_url'),
        ]);

        return response()->json([
            'posting' => new PostingResource($posting),
        ], Response::HTTP_CREATED);
    }

    /**
     * Show one posting.
     */
    public function show(Request $request, Posting $posting): JsonResponse
    {
        $this->authorizeOwnership($request, $posting);

        return response()->json([
            'posting' => new PostingResource($posting),
        ]);
    }

    /**
     * Update posting title or source_url only. Text/parsed_json are immutable —
     * changing them would require re-running the FastAPI pipeline, and users
     * should delete + re-add instead.
     */
    public function update(Request $request, Posting $posting): JsonResponse
    {
        $this->authorizeOwnership($request, $posting);

        $data = $request->validate([
            'title'      => ['nullable', 'string', 'max:255'],
            'source_url' => ['nullable', 'url', 'max:2048'],
        ]);

        $posting->update($data);

        return response()->json([
            'posting' => new PostingResource($posting),
        ]);
    }

    /**
     * Delete the posting.
     */
    public function destroy(Request $request, Posting $posting): JsonResponse
    {
        $this->authorizeOwnership($request, $posting);
        $posting->delete();

        return response()->json(null, Response::HTTP_NO_CONTENT);
    }

    /**
     * Derive a title from the first meaningful line of the posting text.
     * Cheap heuristic — used only when the user didn't supply one.
     */
    private function deriveTitle(string $text): string
    {
        foreach (preg_split('/\R/', $text) as $line) {
            $line = trim($line);
            if (strlen($line) >= 5 && strlen($line) <= 100) {
                return $line;
            }
        }
        return 'Untitled posting';
    }

    private function authorizeOwnership(Request $request, Posting $posting): void
    {
        abort_if($posting->user_id !== $request->user()->id, Response::HTTP_NOT_FOUND);
    }
}
