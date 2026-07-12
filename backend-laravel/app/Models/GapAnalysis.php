<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class GapAnalysis extends Model
{
    use HasFactory;

    protected $fillable = [
        'user_id',
        'resume_version_id',
        'posting_ids_json',
        'ranked_gaps_json',
        'total_postings',
        'computed_at',
    ];

    protected $casts = [
        'posting_ids_json' => 'array',
        'ranked_gaps_json' => 'array',
        'total_postings' => 'integer',
        'computed_at' => 'datetime',
    ];

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    public function resumeVersion(): BelongsTo
    {
        return $this->belongsTo(ResumeVersion::class);
    }
}
