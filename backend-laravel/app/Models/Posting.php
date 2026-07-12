<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Posting extends Model
{
    use HasFactory;

    protected $fillable = [
        'user_id',
        'title',
        'raw_text',
        'parsed_json',
        'source_url',
    ];

    protected $casts = [
        'parsed_json' => 'array',
    ];

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    public function matches(): HasMany
    {
        return $this->hasMany(MatchModel::class);
    }

    public function applications(): HasMany
    {
        return $this->hasMany(Application::class);
    }
}
