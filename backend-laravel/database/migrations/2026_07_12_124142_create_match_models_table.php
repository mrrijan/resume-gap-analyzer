<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('matches', function (Blueprint $table) {
            $table->id();
            $table->foreignId('resume_version_id')->constrained()->cascadeOnDelete();
            $table->foreignId('posting_id')->constrained()->cascadeOnDelete();

            // M3 overall aggregates
            $table->decimal('overall_fit', 5, 2);        // 0.00 - 100.00
            $table->decimal('avg_required', 6, 5);       // 0.00000 - 1.00000
            $table->decimal('avg_preferred', 6, 5)->nullable();
            $table->unsignedTinyInteger('required_weight');
            $table->unsignedTinyInteger('preferred_weight');

            // M3 per-requirement scores + M4 per-posting classification
            $table->json('per_requirement_json');
            $table->json('gap_classification_json')->nullable();

            $table->timestamp('computed_at');
            $table->timestamps();

            $table->index(['resume_version_id', 'posting_id']);
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('match_models');
    }
};
