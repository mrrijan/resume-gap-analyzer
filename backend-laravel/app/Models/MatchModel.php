<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class MatchModel extends Model
{
    use HasFactory;

    /**
     * PHP 8 reserves the class name "Match", so we call this MatchModel.
     * Override Laravel's plural-guessing since it would generate "match_models".
     */
    protected $table = 'matches';

    protected $fillable = [
        'resume_version_id',
        'posting_id',
        'overall_fit',
        'avg_required',
        'avg_preferred',
        'required_weight',
        'preferred_weight',
        'per_requirement_json',
        'gap_classification_json',
        'computed_at',
    ];

    protected $casts = [
        'overall_fit' => 'decimal:2',
        'avg_required' => 'decimal:5',
        'avg_preferred' => 'decimal:5',
        'required_weight' => 'integer',
        'preferred_weight' => 'integer',
        'per_requirement_json' => 'array',
        'gap_classification_json' => 'array',
        'computed_at' => 'datetime',
    ];

    public function resumeVersion(): BelongsTo
    {
        return $this->belongsTo(ResumeVersion::class);
    }

    public function posting(): BelongsTo
    {
        return $this->belongsTo(Posting::class);
    }
}
