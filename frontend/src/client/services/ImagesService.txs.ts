// ImagesService.ts

import { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
import type { ImageOut } from '../models';

export class ImagesService {

    /**
     * Get Images
     * Retrieve all images.
     * @returns ImageOut[] Successful Response
     * @throws ApiError
     */
    public static getImages(): CancelablePromise<ImageOut[]> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/ews/images/',
        });
    }

    /**
     * Upload Image
     * Upload a new image.
     * @param formData FormData containing the image file.
     * @returns ImageOut Successful Response
     * @throws ApiError
     */
    public static uploadStaticImage(formData: FormData): CancelablePromise<ImageOut> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/ews/upload-image/',
            body: formData,
            mediaType: 'multipart/form-data',
            errors: {
                422: `Validation Error`,
                400: `Bad Request`,
                500: `Server Error`,
            },
        });
    }
    public static uploadOfflineImage(formData: FormData): CancelablePromise<ImageOut> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/ews/upload-image/',
            body: formData,
            mediaType: 'multipart/form-data',
            errors: {
                422: `Validation Error`,
                400: `Bad Request`,
                500: `Server Error`,
            },
        });
    }
}
