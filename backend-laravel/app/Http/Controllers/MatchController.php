<?php

namespace App\Http\Controllers;

use App\Http\Requests\MatchStoreRequest;
use App\Http\Resources\MatchResource;
use App\Models\MatchModel;
use App\Models\Posting;
use App\Models\Resume;
use App\Services\FastApiClient;
use App\Services\FastApiException;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Http\Response;

class MatchController extends Controller
{
    public function __construct(private FastApiClient $fastApi) {}

    /**
     * List matches for the authenticated user, optionally filtered.
     * Query params:
     *   ?resume_id=X   — only matches involving this resume
     *   ?posting_id=Y  — only matches involving this posting
     */
    public function index(Request $request): JsonResponse
    {
        $userId = $request->user()->id;

        $query = MatchModel::query()
            ->whereHas('resumeVersion.resume', fn ($q) => $q->where('user_id', $userId))
            ->with('posting')
            ->orderByDesc('overall_fit');

        if ($request->filled('resume_id')) {
            $query->whereHas(
                'resumeVersion',
                fn ($q) => $q->where('resume_id', $request->integer('resume_id'))
            );
        }

        if ($request->filled('posting_id')) {
            $query->where('posting_id', $request->integer('posting_id'));
        }

        return response()->json([
            'matches' => MatchResource::collection($query->get()),
        ]);
    }

    /**
     * Compute a fresh match between a resume's latest version and a posting.
     * If a match already exists for this pair, it's recomputed and overwritten.
     */
    public function store(MatchStoreRequest $request): JsonResponse
    {
        $resume = Resume::with(['versions' => fn ($q) => $q->orderByDesc('version_number')])
            ->findOrFail($request->integer('resume_id'));
        $posting = Posting::findOrFail($request->integer('posting_id'));

        $latestVersion = $resume->versions->first();
        if (! $latestVersion) {
            return response()->json(
                ['message' => 'Resume has no parsed version yet.'],
                Response::HTTP_UNPROCESSABLE_ENTITY,
            );
        }

        // Build the payload FastAPI's /match endpoint expects.
        $parsedResume  = $latestVersion->parsed_json;
        $parsedPosting = $posting->parsed_json;

        $payload = [
            'resume_skills'         => $parsedResume['skills']         ?? [],
            'resume_experience'     => $parsedResume['experience']     ?? [],
            'resume_education'      => $parsedResume['education']      ?? [],
            'resume_certifications' => $parsedResume['certifications'] ?? [],
            'posting_required'      => $parsedPosting['required']      ?? [],
            'posting_preferred'     => $parsedPosting['preferred']     ?? [],
        ];

        try {
            $result = $this->fastApi->match($payload);
        } catch (FastApiException $e) {
            return response()->json(
                ['message' => 'Failed to compute match.'],
                Response::HTTP_BAD_GATEWAY,
            );
        }

        // Compute M4a classification here so downstream reads don't have to.
        $classification = $this->classifyRequirements($result['per_requirement']);

        // Upsert: recomputing the same pair overwrites the previous match.
        $match = MatchModel::updateOrCreate(
            [
                'resume_version_id' => $latestVersion->id,
                'posting_id'        => $posting->id,
            ],
            [
                'overall_fit'             => $result['overall_fit'],
                'avg_required'            => $result['avg_required'],
                'avg_preferred'           => $result['avg_preferred'] ?? null,
                'required_weight'         => $result['required_weight'],
                'preferred_weight'        => $result['preferred_weight'],
                'per_requirement_json'    => $result['per_requirement'],
                'gap_classification_json' => $classification,
                'computed_at'             => now(),
            ]
        );

        $match->load('posting');

        return response()->json([
            'match' => new MatchResource($match),
        ], Response::HTTP_CREATED);
    }

    public function show(Request $request, MatchModel $match): JsonResponse
    {
        $this->authorizeOwnership($request, $match);
        $match->load('posting');

        return response()->json([
            'match' => new MatchResource($match),
        ]);
    }

    /**
     * Matches are recomputed, not manually edited.
     */
    public function update(Request $request, MatchModel $match): JsonResponse
    {
        return response()->json(
            ['message' => 'Matches cannot be edited directly. Recompute via POST /matches instead.'],
            Response::HTTP_METHOD_NOT_ALLOWED,
        );
    }

    public function destroy(Request $request, MatchModel $match): JsonResponse
    {
        $this->authorizeOwnership($request, $match);
        $match->delete();

        return response()->json(null, Response::HTTP_NO_CONTENT);
    }

    /**
     * Classify each per-requirement match as strong/partial/missing based on
     * similarity thresholds. This mirrors M4a's Python implementation — kept
     * in sync so pre-M4 UI can show classifications without a round trip.
     *
     * If you change the thresholds, update:
     *   - ml-service/config/gap_analysis.py (source of truth)
     *   - this method (Laravel-side mirror)
     */
    private const STRONG_THRESHOLD  = 0.60;
    private const PARTIAL_THRESHOLD = 0.35;

    private function classifyRequirements(array $perRequirement): array
    {
        return array_map(function (array $req) {
            $sim = (float) $req['similarity'];
            $strength = match (true) {
                $sim >= self::STRONG_THRESHOLD  => 'strong',
                $sim >= self::PARTIAL_THRESHOLD => 'partial',
                default                          => 'missing',
            };
            return [...$req, 'strength' => $strength];
        }, $perRequirement);
    }

    /**
     * Guard: user only sees their own matches (via ownership of the resume).
     */
    private function authorizeOwnership(Request $request, MatchModel $match): void
    {
        $userId = $match->resumeVersion?->resume?->user_id;
        abort_if($userId !== $request->user()->id, Response::HTTP_NOT_FOUND);
    }
}
