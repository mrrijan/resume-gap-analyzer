<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class ResumeVersion extends Model
{
    use HasFactory;

    protected $fillable = [
        'resume_id',
        'version_number',
        'parsed_json',
    ];

    protected $casts = [
        'parsed_json' => 'array',
    ];

    public function resume(): BelongsTo
    {
        return $this->belongsTo(Resume::class);
    }

    public function matches(): HasMany
    {
        return $this->hasMany(MatchModel::class, 'resume_version_id');
    }
}
