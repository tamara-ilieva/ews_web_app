import axios from 'axios';
import { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
import type { ImageOut } from '../models';

const API_URL = 'http://localhost:8008/api/v1/ews';

export class ImagesService {
    public static getImages(): CancelablePromise<ImageOut[]> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/ews/images/',
        });
    }

    public static getDynamicImages(): CancelablePromise<ImageOut[]> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/ews/dynamic-images/',
        });
    }

    public static getStaticImages(): CancelablePromise<ImageOut[]> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/ews/static-images/',
        });
    }

    public static getUploadedImages(): CancelablePromise<ImageOut[]> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/ews/uploaded-images/',
        });
    }

    public static getAllDiseases(): CancelablePromise<Disease[]> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/ews/diseases/',
        });
    }

    public static uploadStaticImage(formData: FormData): CancelablePromise<ImageOut> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/ews/upload-image-static/',
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
            url: '/api/v1/ews/upload-image-uploaded/',
            body: formData,
            mediaType: 'multipart/form-data',
            errors: {
                422: `Validation Error`,
                400: `Bad Request`,
                500: `Server Error`,
            },
        });
    }

    public static changeIsSick = async (type, imageId, isSick) => {
        const response = await axios.post(`${API_URL}/change-is-sick`, {
            type,
            image_id: imageId,
            is_sick_human_input: isSick,
        });
        return response.data;
    };

    public static changeDisease = async (type, imageId, diseaseId) => {
        console.log(type, imageId, diseaseId)
        const response = await axios.post(`${API_URL}/change-disease`, {
            type: type,
            image_id: imageId,
            disease_id: diseaseId,
        });
        return response.data;
    };
}

export default ImagesService