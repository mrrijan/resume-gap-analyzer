<?php

use App\Http\Controllers\AuthController;
use App\Http\Controllers\GapAnalysisController;
use App\Http\Controllers\MatchController;
use App\Http\Controllers\PostingController;
use App\Http\Controllers\ResumeController;
use Illuminate\Support\Facades\Route;

// Public auth routes
Route::post('/register', [AuthController::class, 'register']);
Route::post('/login',    [AuthController::class, 'login']);

// Authenticated routes
Route::middleware('auth:sanctum')->group(function () {
    Route::post('/logout', [AuthController::class, 'logout']);
    Route::get('/me',      [AuthController::class, 'me']);

    Route::apiResource('resumes', ResumeController::class);
    Route::apiResource('postings', PostingController::class);
    Route::apiResource('matches', MatchController::class);
    Route::apiResource('gap-analyses', GapAnalysisController::class);
    Route::put('/change-password', [AuthController::class, 'changePassword']);
});
