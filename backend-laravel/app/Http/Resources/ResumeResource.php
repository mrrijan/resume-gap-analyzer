<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class ResumeResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return [
            'id'                => $this->id,
            'original_filename' => $this->original_filename,
            'created_at'        => $this->created_at?->toIso8601String(),
            'updated_at'        => $this->updated_at?->toIso8601String(),

            // Include the latest version if loaded (avoids extra queries when it wasn't).
            'latest_version'    => new ResumeVersionResource(
                $this->whenLoaded('versions', fn () => $this->versions->sortByDesc('version_number')->first())
            ),
        ];
    }
}
