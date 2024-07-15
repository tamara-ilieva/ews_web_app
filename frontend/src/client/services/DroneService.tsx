/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ApiError } from '../models/ApiError';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class DroneService {

    /**
     * Get Drone Pictures Number
     * Retrieve the number of drone pictures.
     * @returns { number: number } Successful Response
     * @throws ApiError
     */
    public static getDronePicturesNum(): CancelablePromise<{ number: number }> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/drone/num-pictures',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Update Drone Pictures Number
     * Update the number of drone pictures.
     * @returns { number: number } Successful Response
     * @throws ApiError
     */
    public static updateDronePicturesNum({
        requestBody,
    }: {
        requestBody: { number: number },
    }): CancelablePromise<{ number: number }> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/drone/num-pictures',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

}
