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
        Schema::create('gap_analyses', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->foreignId('resume_version_id')->constrained()->cascadeOnDelete();

            $table->json('posting_ids_json');   // snapshot of which postings were included
            $table->json('ranked_gaps_json');   // M4b output
            $table->unsignedInteger('total_postings');

            $table->timestamp('computed_at');
            $table->timestamps();

            $table->index(['user_id', 'resume_version_id']);
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('gap_analyses');
    }
};
