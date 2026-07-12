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
        Schema::create('applications', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->foreignId('posting_id')->constrained()->cascadeOnDelete();

            $table->enum('status', ['applied', 'interview', 'rejected', 'offered'])
                ->default('applied');
            $table->text('notes')->nullable();
            $table->timestamp('applied_at')->nullable();

            $table->timestamps();

            $table->index(['user_id', 'status']);
            $table->unique(['user_id', 'posting_id']);
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('applications');
    }
};
