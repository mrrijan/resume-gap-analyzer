<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class GapAnalysisResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return [
            'id'                => $this->id,
            'resume_version_id' => $this->resume_version_id,
            'posting_ids'       => $this->posting_ids_json,
            'ranked_gaps'       => $this->ranked_gaps_json,
            'total_postings'    => $this->total_postings,
            'computed_at'       => $this->computed_at?->toIso8601String(),
            'created_at'        => $this->created_at?->toIso8601String(),
        ];
    }
}
