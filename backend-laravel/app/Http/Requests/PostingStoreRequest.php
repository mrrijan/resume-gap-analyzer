<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class PostingStoreRequest extends FormRequest
{
    public function authorize(): bool
    {
        return $this->user() !== null;
    }

    public function rules(): array
    {
        return [
            'title'      => ['nullable', 'string', 'max:255'],
            'text'       => ['required', 'string', 'min:50', 'max:20000'],
            'source_url' => ['nullable', 'url', 'max:2048'],
        ];
    }

    public function messages(): array
    {
        return [
            'text.min' => 'Job posting text is too short — please paste the full description.',
            'text.max' => 'Job posting text is too long (max 20,000 characters).',
        ];
    }
}
