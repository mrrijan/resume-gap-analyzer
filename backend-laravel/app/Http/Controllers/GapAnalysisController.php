<?php

namespace App\Http\Controllers;

use App\Http\Requests\GapAnalysisStoreRequest;
use App\Http\Resources\GapAnalysisResource;
use App\Models\GapAnalysis;
use App\Models\MatchModel;
use App\Models\Resume;
use App\Services\FastApiClient;
use App\Services\FastApiException;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Http\Response;

class GapAnalysisController extends Controller
{
    public function __construct(private FastApiClient $fastApi) {}

    /**
     * List all gap analysis runs for the authenticated user.
     */
    public function index(Request $request): JsonResponse
    {
        $analyses = GapAnalysis::query()
            ->where('user_id', $request->user()->id)
            ->orderByDesc('computed_at')
            ->get();

        return response()->json([
            'gap_analyses' => GapAnalysisResource::collection($analyses),
        ]);
    }

    /**
     * Run gap analysis across the specified postings for a resume.
     *
     * Requires matches to already exist for each (resume_latest_version, posting)
     * pair. Callers compute matches individually via POST /matches first.
     */
    public function store(GapAnalysisStoreRequest $request): JsonResponse
    {
        $userId = $request->user()->id;
        $postingIds = $request->input('posting_ids');

        // Load resume and its latest version.
        $resume = Resume::with(['versions' => fn ($q) => $q->orderByDesc('version_number')])
            ->findOrFail($request->integer('resume_id'));

        $latestVersion = $resume->versions->first();
        if (! $latestVersion) {
            return response()->json(
                ['message' => 'Resume has no parsed version yet.'],
                Response::HTTP_UNPROCESSABLE_ENTITY,
            );
        }

        // Pull matches for the requested postings.
        $matches = MatchModel::query()
            ->where('resume_version_id', $latestVersion->id)
            ->whereIn('posting_id', $postingIds)
            ->get();

        // Check that we have a match for every requested posting.
        $foundPostingIds = $matches->pluck('posting_id')->all();
        $missingPostingIds = array_values(array_diff($postingIds, $foundPostingIds));

        if (! empty($missingPostingIds)) {
            return response()->json([
                'message' => 'Some postings do not have a computed match yet. '
                    . 'Compute matches first via POST /matches.',
                'missing_posting_ids' => $missingPostingIds,
            ], Response::HTTP_UNPROCESSABLE_ENTITY);
        }

        // Assemble the FastAPI payload — one entry per posting match.
        $postingMatches = $matches->map(function (MatchModel $match) {
            return [
                'posting_id'   => (string) $match->posting_id,
                'match_result' => [
                    'overall_fit'       => (float) $match->overall_fit,
                    'avg_required'      => (float) $match->avg_required,
                    'avg_preferred'     => $match->avg_preferred !== null ? (float) $match->avg_preferred : 0.0,
                    'required_weight'   => $match->required_weight,
                    'preferred_weight'  => $match->preferred_weight,
                    'per_requirement'   => $match->per_requirement_json,
                ],
            ];
        })->values()->all();

        try {
            $result = $this->fastApi->gapAnalysis($postingMatches);
        } catch (FastApiException $e) {
            return response()->json(
                ['message' => 'Failed to compute gap analysis.'],
                Response::HTTP_BAD_GATEWAY,
            );
        }

        $analysis = GapAnalysis::create([
            'user_id'           => $userId,
            'resume_version_id' => $latestVersion->id,
            'posting_ids_json'  => $postingIds,
            'ranked_gaps_json'  => $result['ranked_gaps'],
            'total_postings'    => $result['total_postings'],
            'computed_at'       => now(),
        ]);

        return response()->json([
            'gap_analysis' => new GapAnalysisResource($analysis),
        ], Response::HTTP_CREATED);
    }

    public function show(Request $request, GapAnalysis $gap_analysis): JsonResponse
    {
        $this->authorizeOwnership($request, $gap_analysis);

        return response()->json([
            'gap_analysis' => new GapAnalysisResource($gap_analysis),
        ]);
    }

    public function update(Request $request, GapAnalysis $gap_analysis): JsonResponse
    {
        return response()->json(
            ['message' => 'Gap analyses cannot be edited. Run a new one instead.'],
            Response::HTTP_METHOD_NOT_ALLOWED,
        );
    }

    public function destroy(Request $request, GapAnalysis $gap_analysis): JsonResponse
    {
        $this->authorizeOwnership($request, $gap_analysis);
        $gap_analysis->delete();

        return response()->json(null, Response::HTTP_NO_CONTENT);
    }

    private function authorizeOwnership(Request $request, GapAnalysis $analysis): void
    {
        abort_if($analysis->user_id !== $request->user()->id, Response::HTTP_NOT_FOUND);
    }
}
