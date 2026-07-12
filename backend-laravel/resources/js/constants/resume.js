/**
 * Resume upload configuration.
 * Mirrors the Laravel FormRequest rules — keep in sync.
 */
export const RESUME_UPLOAD = {
    acceptedTypes: '.pdf,.docx',
    acceptedMimeTypes: [
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    ],
    maxSizeMb: 5,
    maxSizeBytes: 5 * 1024 * 1024,
};
