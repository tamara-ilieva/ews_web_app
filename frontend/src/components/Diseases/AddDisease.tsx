import {
    Button,
    FormControl,
    FormErrorMessage,
    FormLabel,
    Input,
    Modal,
    ModalBody,
    ModalCloseButton,
    ModalContent,
    ModalFooter,
    ModalHeader,
    ModalOverlay,
    Textarea,
} from "@chakra-ui/react"
import type React from "react"
import {type SubmitHandler, useForm} from "react-hook-form"
import {useMutation, useQueryClient} from "react-query"

import {type ApiError, type DiseaseCreate, DiseasesService} from "../../client"
import useCustomToast from "../../hooks/useCustomToast"

interface AddDiseaseProps {
    isOpen: boolean
    onClose: () => void
}

const AddDisease: React.FC<AddDiseaseProps> = ({isOpen, onClose}) => {
    const queryClient = useQueryClient()
    const showToast = useCustomToast()
    const {
        register,
        handleSubmit,
        reset,
        formState: {errors, isSubmitting},
    } = useForm<DiseaseCreate>({
        mode: "onBlur",
        criteriaMode: "all",
        defaultValues: {
            name: "",
            description: "",
            healing_steps: "",
        },
    })

    const addDisease = async (data: DiseaseCreate) => {
        await DiseasesService.createDisease({requestBody: data})
    }

    const mutation = useMutation(addDisease, {
        onSuccess: () => {
            showToast("Success!", "Disease added successfully.", "success");
            reset();
            onClose();
        },
        onError: (err: ApiError) => {
            // Log the error to see its structure
            console.error(err);

            // Extracting error details and converting it to a string if necessary
            const errDetail = err instanceof Error ? err.message : 'An unexpected error occurred';
            showToast("Something went wrong.", errDetail, "error");
        },
        onSettled: () => {
            queryClient.invalidateQueries("diseases");
        },
    });

    const onSubmit: SubmitHandler<DiseaseCreate> = (data) => {
        mutation.mutate(data)
    }

    return (
        <>
            <Modal
                isOpen={isOpen}
                onClose={onClose}
                size={{base: "sm", md: "md"}}
                isCentered
            >
                <ModalOverlay/>
                <ModalContent as="form" onSubmit={handleSubmit(onSubmit)}>
                    <ModalHeader>Add Disease</ModalHeader>
                    <ModalCloseButton/>
                    <ModalBody pb={6}>
                        <FormControl isRequired isInvalid={!!errors.name}>
                            <FormLabel htmlFor="name">Name</FormLabel>
                            <Input
                                id="name"
                                {...register("name", {
                                    required: "Name is required.",
                                })}
                                placeholder="Name"
                                type="text"
                            />
                            {errors.name && (
                                <FormErrorMessage>{errors.name.message}</FormErrorMessage>
                            )}
                        </FormControl>
                        <FormControl mt={4}>
                            <FormLabel htmlFor="description">Description</FormLabel>
                            <Textarea
                                id="description"
                                {...register("description")}
                                placeholder="Description"
                            />
                        </FormControl>
                        <FormControl mt={4}>
                            <FormLabel htmlFor="healing_steps">Healing Steps</FormLabel>
                            <Textarea
                                id="healing_steps"
                                {...register("healing_steps")}
                                placeholder="Healing Steps"
                            />
                        </FormControl>
                    </ModalBody>

                    <ModalFooter gap={3}>
                        <Button variant="primary" type="submit" isLoading={isSubmitting}>
                            Save
                        </Button>
                        <Button onClick={onClose}>Cancel</Button>
                    </ModalFooter>
                </ModalContent>
            </Modal>
        </>
    )
}

export default AddDisease
