<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

class GapAnalysisStoreRequest extends FormRequest
{
    public function authorize(): bool
    {
        return $this->user() !== null;
    }

    public function rules(): array
    {
        $userId = $this->user()->id;

        return [
            'resume_id' => [
                'required',
                'integer',
                Rule::exists('resumes', 'id')->where('user_id', $userId),
            ],
            'posting_ids' => [
                'required',
                'array',
                'min:1',
            ],
            'posting_ids.*' => [
                'integer',
                Rule::exists('postings', 'id')->where('user_id', $userId),
            ],
        ];
    }

    public function messages(): array
    {
        return [
            'posting_ids.required' => 'At least one posting is required for gap analysis.',
            'posting_ids.min'      => 'At least one posting is required for gap analysis.',
        ];
    }
}
