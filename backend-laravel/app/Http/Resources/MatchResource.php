<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class MatchResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return [
            'id'                     => $this->id,
            'resume_version_id'      => $this->resume_version_id,
            'posting_id'             => $this->posting_id,

            'overall_fit'            => (float) $this->overall_fit,
            'avg_required'           => (float) $this->avg_required,
            'avg_preferred'          => $this->avg_preferred !== null ? (float) $this->avg_preferred : null,
            'required_weight'        => $this->required_weight,
            'preferred_weight'       => $this->preferred_weight,

            'per_requirement'        => $this->per_requirement_json,
            'gap_classification'     => $this->gap_classification_json,

            'computed_at'            => $this->computed_at?->toIso8601String(),

            // Optional joined data when loaded.
            'posting' => new PostingResource($this->whenLoaded('posting')),
        ];
    }
}
