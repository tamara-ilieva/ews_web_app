/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DiseaseCreate } from '../models/DiseaseCreate';
import type { DiseaseOut } from '../models/DiseaseOut';
import type { DiseasesOut } from '../models/DiseasesOut';
import type { DiseaseUpdate } from '../models/DiseaseUpdate';
import type { Message } from '../models/Message';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class DiseasesService {

    /**
     * Read Diseases
     * Retrieve diseases.
     * @returns DiseasesOut Successful Response
     * @throws ApiError
     */
    public static readDiseases({
        skip,
        limit = 100,
    }: {
        skip?: number,
        limit?: number,
    }): CancelablePromise<DiseasesOut> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/ews/diseases/',
            /*query: {
                'skip': skip,
                'limit': limit,
            },*/
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Create Disease
     * Create new disease.
     * @returns DiseaseOut Successful Response
     * @throws ApiError
     */
    public static createDisease({
        requestBody,
    }: {
        requestBody: DiseaseCreate,
    }): CancelablePromise<DiseaseOut> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/ews/diseases/',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Read Disease
     * Get disease by ID.
     * @returns DiseaseOut Successful Response
     * @throws ApiError
     */
    public static readDisease({
        id,
    }: {
        id: number,
    }): CancelablePromise<DiseaseOut> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/diseases/{id}',
            path: {
                'id': id,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Update Disease
     * Update a disease.
     * @returns DiseaseOut Successful Response
     * @throws ApiError
     */
    public static updateDisease({
        id,
        requestBody,
    }: {
        id: number,
        requestBody: DiseaseUpdate,
    }): CancelablePromise<DiseaseOut> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/diseases/{id}',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Delete Disease
     * Delete a disease.
     * @returns Message Successful Response
     * @throws ApiError
     */
    public static deleteDisease({
        id,
    }: {
        id: number,
    }): CancelablePromise<Message> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/diseases/{id}',
            path: {
                'id': id,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

}
