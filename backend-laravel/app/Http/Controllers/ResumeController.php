<?php

namespace App\Http\Controllers;

use App\Http\Requests\ResumeStoreRequest;
use App\Http\Resources\ResumeResource;
use App\Models\Resume;
use App\Models\ResumeVersion;
use App\Services\FastApiClient;
use App\Services\FastApiException;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Http\Response;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Storage;

class ResumeController extends Controller
{
    public function __construct(private FastApiClient $fastApi) {}

    /**
     * List all resumes belonging to the authenticated user.
     */
    public function index(Request $request): JsonResponse
    {
        $resumes = Resume::query()
            ->where('user_id', $request->user()->id)
            ->with(['versions' => fn ($q) => $q->orderByDesc('version_number')])
            ->orderByDesc('created_at')
            ->get();

        return response()->json([
            'resumes' => ResumeResource::collection($resumes),
        ]);
    }

    /**
     * Upload a resume file, parse it via FastAPI, create Resume + first ResumeVersion.
     */
    public function store(ResumeStoreRequest $request): JsonResponse
    {
        $file = $request->file('file');
        $userId = $request->user()->id;

        // Call FastAPI first — if parsing fails, we don't want a half-created record.
        try {
            $parsed = $this->fastApi->parseResume(
                file_get_contents($file->getRealPath()),
                $file->getClientOriginalName(),
            );
        } catch (FastApiException $e) {
            return response()->json([
                'message' => 'Failed to parse resume. Please try a different file.',
            ], Response::HTTP_BAD_GATEWAY);
        }

        // Parsing succeeded — persist file + records in a transaction.
        $storagePath = $file->store("resumes/{$userId}");

        $resume = DB::transaction(function () use ($userId, $file, $storagePath, $parsed) {
            $resume = Resume::create([
                'user_id'           => $userId,
                'original_filename' => $file->getClientOriginalName(),
                'storage_path'      => $storagePath,
            ]);

            ResumeVersion::create([
                'resume_id'      => $resume->id,
                'version_number' => 1,
                'parsed_json'    => $parsed,
            ]);

            return $resume->load(['versions' => fn ($q) => $q->orderByDesc('version_number')]);
        });

        return response()->json([
            'resume' => new ResumeResource($resume),
        ], Response::HTTP_CREATED);
    }

    /**
     * Show one resume with all its versions.
     */
    public function show(Request $request, Resume $resume): JsonResponse
    {
        $this->authorizeOwnership($request, $resume);

        $resume->load(['versions' => fn ($q) => $q->orderByDesc('version_number')]);

        return response()->json([
            'resume' => new ResumeResource($resume),
        ]);
    }

    /**
     * Update is not currently supported for resumes.
     * Users create new versions instead (via re-upload, S4 stretch).
     */
    public function update(Request $request, Resume $resume): JsonResponse
    {
        return response()->json(
            ['message' => 'Resume updates are not supported. Upload a new version instead.'],
            Response::HTTP_METHOD_NOT_ALLOWED,
        );
    }

    /**
     * Delete the resume, its versions, and the underlying file.
     */
    public function destroy(Request $request, Resume $resume): JsonResponse
    {
        $this->authorizeOwnership($request, $resume);

        // Delete the physical file from disk (DB cascade handles the versions).
        Storage::delete($resume->storage_path);
        $resume->delete();

        return response()->json(null, Response::HTTP_NO_CONTENT);
    }

    /**
     * Guard: throw 404 (not 403) if the resume doesn't belong to this user.
     * 404 hides the existence of other users' records — better than "you can't touch this."
     */
    private function authorizeOwnership(Request $request, Resume $resume): void
    {
        abort_if($resume->user_id !== $request->user()->id, Response::HTTP_NOT_FOUND);
    }
}
