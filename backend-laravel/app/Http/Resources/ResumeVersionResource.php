<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class ResumeVersionResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return [
            'id'             => $this->id,
            'version_number' => $this->version_number,
            'parsed'         => $this->parsed_json,
            'created_at'     => $this->created_at?->toIso8601String(),
        ];
    }
}
