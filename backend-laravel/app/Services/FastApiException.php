<?php

namespace App\Services;

use Exception;

/**
 * Thrown when the FastAPI ML service call fails or returns an unexpected shape.
 * Controllers catch this to convert into HTTP 502 (bad gateway) responses.
 */
class FastApiException extends Exception
{
}
