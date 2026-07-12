<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

class MatchStoreRequest extends FormRequest
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
            'posting_id' => [
                'required',
                'integer',
                Rule::exists('postings', 'id')->where('user_id', $userId),
            ],
        ];
    }

    public function messages(): array
    {
        return [
            'resume_id.exists'  => 'Resume not found.',
            'posting_id.exists' => 'Posting not found.',
        ];
    }
}
