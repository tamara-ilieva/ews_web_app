import React from 'react';
import {
    Button,
    FormControl,
    FormLabel,
    Input,
    Modal,
    ModalBody,
    ModalCloseButton,
    ModalContent,
    ModalFooter,
    ModalHeader,
    ModalOverlay,
} from "@chakra-ui/react";
import { useForm } from "react-hook-form";
import { useMutation, useQueryClient } from 'react-query';

import useCustomToast from "../../hooks/useCustomToast";
import { ImagesService } from "../../client";

interface AddImageProps {
    isOpen: boolean;
    onClose: () => void;
}

const AddStaticImage: React.FC<AddImageProps> = ({ isOpen, onClose }) => {
    const queryClient = useQueryClient();
    const showToast = useCustomToast();
    const { register, handleSubmit, setValue, reset, formState: { isSubmitting } } = useForm<{ image: FileList }>({
        mode: "onTouched",
    });

    // Register the 'image' field dynamically
    React.useEffect(() => {
        register('image', { required: true });
    }, [register]);

    const mutation = useMutation((formData: FormData) => ImagesService.uploadOfflineImage(formData), {
        onSuccess: () => {
            showToast("Success!", "Image uploaded successfully.", "success");
            reset();
            onClose();
        },
        onError: (error: any) => {
            showToast("Error", "Failed to upload image.", "error");
            console.error('Upload error:', error);
        },
        onSettled: () => {
            queryClient.invalidateQueries("images");
        },
    });

    const onSubmit = async (data) => {
        const formData = new FormData();
        formData.append('image', data.image[0]);
        mutation.mutate(formData);
    };

    const handleImageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        console.log('File chosen:', event.target.files);
        const files = event.target.files;
        if (files && files.length > 0) {
            setValue('image', files);
        }
    };

    return (
        <Modal isOpen={isOpen} onClose={onClose} isCentered>
            <ModalOverlay/>
            <ModalContent as="form" onSubmit={handleSubmit(onSubmit)}>
                <ModalHeader>Add Image</ModalHeader>
                <ModalCloseButton/>
                <ModalBody pb={6}>
                    <FormControl isRequired>
                        <FormLabel htmlFor="image">Upload Image</FormLabel>
                        <Input id="image" type="file" onChange={handleImageChange}/>
                    </FormControl>
                </ModalBody>
                <ModalFooter gap={3}>
                    <Button colorScheme="blue" type="submit" isLoading={isSubmitting}>
                        Upload
                    </Button>
                    <Button onClick={onClose}>Cancel</Button>
                </ModalFooter>
            </ModalContent>
        </Modal>
    );
};

export default AddStaticImage;
